import json
from fastapi import APIRouter, HTTPException
import mysql.connector
from pydantic import BaseModel

items_router = APIRouter(prefix="/items", tags=["Items"])
users_router = APIRouter(prefix="/users", tags=["Users"])
cart_router = APIRouter(prefix="/cart", tags=["Cart"])
reviews_router = APIRouter(prefix="/reviews", tags=["Reviews"])

db = mysql.connector.connect(
    host='sql12.freesqldatabase.com',
    user='sql12737673',
    passwd='8xZfPQcWFa',
    database='sql12737673',
)

c = db.cursor(dictionary=True)

table_name = "robocat_items"
user_table_name = "robocat_users"
cart_table_name = "robocat_cart"
reviews_table_name = "robocat_reviews"

c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ("
          f"id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,"
          f"name VARCHAR(255) NOT NULL,"
          f"image_url VARCHAR(255) NOT NULL,"
          f"price DOUBLE NOT NULL)")

c.execute(f"CREATE TABLE IF NOT EXISTS {user_table_name} ("
          f"id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,"
          f"username VARCHAR(255) NOT NULL,"
          f"password VARCHAR(255) NOT NULL)"
          )

c.execute(f"CREATE TABLE IF NOT EXISTS {cart_table_name} ("
          f"username VARCHAR(255) NOT NULL,"
          f"cartcontent VARCHAR(511) NOT NULL)"
          )

c.execute(f"CREATE TABLE IF NOT EXISTS {reviews_table_name} ("
          f"id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,"
          f"username VARCHAR(255) NOT NULL,"
          f"content VARCHAR(511) NOT NULL)"
          )


class Item(BaseModel):
    name: str
    image_url: str
    price: float


class User(BaseModel):
    username: str
    password: str


class CartItem(BaseModel):
    username: str
    cartcontent: list


class Review(BaseModel):
    username: str
    content: str


@items_router.get("/")
async def get_items():
    c.execute(f"SELECT * "
              f"FROM {table_name}")
    data = c.fetchall()
    return data


@items_router.post("/")
async def create_item(new_item: Item):
    c.execute(f"INSERT INTO {table_name} (name, image_url, price) "
              f"VALUES ('{new_item.name}', '{new_item.image_url}', '{new_item.price}')")
    db.commit()
    return new_item


@items_router.delete("/{item_id}")
async def delete_item(item_id: int):
    sql_query = (f"DELETE FROM {table_name} "
                 f"WHERE id='{item_id}'")
    c.execute(sql_query)
    db.commit()
    if c.rowcount > 0:
        return {"message": "Deleted"}
    else:
        raise HTTPException(status_code=404, detail=f"Item not found with id {item_id}")


@users_router.get('/')
async def get_users():
    c.execute(f"SELECT * "
              f"FROM {user_table_name}")
    data = c.fetchall()
    return data


@users_router.post('/register')
async def create_user(new_user: User):
    c.execute(f"SELECT * FROM {user_table_name} "
              f"WHERE username='{new_user.username}'")
    c.fetchall()
    if c.rowcount == 0:
        c.execute(f"INSERT INTO {user_table_name} (username, password) "
                  f"VALUES ('{new_user.username}', '{new_user.password}')")
        db.commit()

        c.execute(f"INSERT INTO {cart_table_name} (username, cartcontent)"
                  f"VALUES ('{new_user.username}', '[]')")
        db.commit()
        return new_user
    else:
        raise HTTPException(status_code=409, detail=f"User already exists")


@users_router.post('/login')
async def login_user(user: User):
    c.execute(f"SELECT * FROM {user_table_name} "
              f"WHERE username='{user.username}'")
    data = c.fetchall()[0]
    if c.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"No User Found!")

    if (data['username'] != user.username
            or data['password'] != user.password):
        raise HTTPException(status_code=404, detail=f"Incorrect credentials!")
    else:
        return {"message": "Logged in successfully"}


@cart_router.get('/{username}')
async def get_cart(username: str):
    c.execute(f"SELECT * FROM {cart_table_name} "
              f"WHERE username = '{username}'")
    data = c.fetchall()
    return data


@cart_router.post('/')
async def add_to_cart(cart_item: CartItem):
    c.execute(f"UPDATE {cart_table_name} "
              f"SET cartcontent = '{json.dumps(cart_item.cartcontent)}' "
              f"WHERE username = '{cart_item.username}'")
    db.commit()
    return {"message": "Updated"}


@reviews_router.get("/")
async def get_reviews():
    c.execute(f"SELECT * FROM {reviews_table_name} ")
    data = c.fetchall()
    return data


@reviews_router.post('/')
async def add_review(review: Review):
    c.execute(f"INSERT INTO {reviews_table_name} (username, content) "
              f"VALUES ('{review.username}', '{review.content}')")
    db.commit()
    return {"message": "Successfully added"}


@reviews_router.delete('/{review_id}')
async def delete_review(review_id: int):
    c.execute(f"DELETE FROM {reviews_table_name} "
              f"WHERE id='{review_id}'")
    db.commit()
    if c.rowcount > 0:
        return {"message": "Deleted"}
    else:
        raise HTTPException(status_code=404, detail=f"Review not found with id {review_id}")

