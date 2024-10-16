from fastapi import FastAPI
from items import items_router, users_router, cart_router, reviews_router
from fastapi.middleware.cors import CORSMiddleware

import pyjokes

app = FastAPI()
app.include_router(items_router)
app.include_router(users_router)
app.include_router(cart_router)
app.include_router(reviews_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Дозволяє всім доменам робити запити
    allow_credentials=True,
    allow_methods=["*"],  # Дозволяє всі HTTP методи (GET, POST і т.д.)
    allow_headers=["*"],  # Дозволяє всі заголовки
)


@app.get("/")
def root():
    return {"message": pyjokes.get_joke()}
