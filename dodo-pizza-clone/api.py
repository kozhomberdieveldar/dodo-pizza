from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Pizza(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image: str

class CartItem(BaseModel):
    pizza_id: int
    quantity: int

class User(BaseModel):
    username: str
    password: str

# Mock database
pizzas_db = [
    {
        "id": 1,
        "name": "Пепперони",
        "description": "Пикантная пепперони, увеличенная порция моцареллы, томатный соус",
        "price": 395,
        "image": "https://dodopizza-a.akamaihd.net/static/Img/Products/Pizza/ru-RU/2ffc31bb-132c-4c99-b894-53f7107a1441.jpg"
    },
    {
        "id": 2,
        "name": "Маргарита",
        "description": "Увеличенная порция моцареллы, томаты, итальянские травы, томатный соус",
        "price": 395,
        "image": "https://dodopizza-a.akamaihd.net/static/Img/Products/Pizza/ru-RU/6652fec1-04df-49ba-b554-3ea30b6e701d.jpg"
    },
    {
        "id": 3,
        "name": "Четыре сыра",
        "description": "Сыр блю чиз, сыр чеддер, моцарелла, сыр чеддер, соус альфредо",
        "price": 395,
        "image": "https://dodopizza-a.akamaihd.net/static/Img/Products/Pizza/ru-RU/af553bf5-3887-4761-b92a-1968e9cdd1b2.jpg"
    }
]

cart_db = []
users_db = []

# API endpoints
@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API Додо Пиццы!"}

@app.get("/pizzas", response_model=List[Pizza])
def get_pizzas():
    return pizzas_db

@app.get("/pizzas/{pizza_id}", response_model=Pizza)
def get_pizza(pizza_id: int):
    pizza = next((p for p in pizzas_db if p["id"] == pizza_id), None)
    if pizza is None:
        raise HTTPException(status_code=404, detail="Пицца не найдена")
    return pizza

@app.post("/cart/add")
def add_to_cart(item: CartItem):
    pizza = next((p for p in pizzas_db if p["id"] == item.pizza_id), None)
    if pizza is None:
        raise HTTPException(status_code=404, detail="Пицца не найдена")
    
    cart_item = next((i for i in cart_db if i["pizza_id"] == item.pizza_id), None)
    if cart_item:
        cart_item["quantity"] += item.quantity
    else:
        cart_db.append({"pizza_id": item.pizza_id, "quantity": item.quantity})
    
    return {"message": "Пицца добавлена в корзину", "cart": cart_db}

@app.get("/cart")
def get_cart():
    cart_items = []
    total = 0
    for item in cart_db:
        pizza = next((p for p in pizzas_db if p["id"] == item["pizza_id"]), None)
        if pizza:
            cart_items.append({
                "pizza": pizza,
                "quantity": item["quantity"],
                "subtotal": pizza["price"] * item["quantity"]
            })
            total += pizza["price"] * item["quantity"]
    return {"items": cart_items, "total": total}

@app.post("/cart/clear")
def clear_cart():
    cart_db.clear()
    return {"message": "Корзина очищена"}

@app.post("/auth/register")
def register(user: User):
    if any(u["username"] == user.username for u in users_db):
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    users_db.append({"username": user.username, "password": user.password})
    return {"message": "Пользователь успешно зарегистрирован"}

@app.post("/auth/login")
def login(user: User):
    if not any(u["username"] == user.username and u["password"] == user.password for u in users_db):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    return {"message": "Успешный вход"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 