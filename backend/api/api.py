from fastapi import FastAPI
import json
from backend.auth.auth_handler import signJWT

app = FastAPI()
users = []


def check_user(data: dict) -> bool:
    for user in users:
        if user["email"] == data["email"] and user["password"] == data["password"]:
            return True
    return False


@app.get('/')
async def root():
    return {'message': 'Hello World!'}


@app.post('/signup')
async def create_user(user: str):
    user_dict = json.loads(user)
    print(user_dict)
    users.append(user_dict)
    return signJWT(user_dict["email"])


@app.post('/login')
async def login(user: str):
    user_dict = json.loads(user)
    if check_user(user_dict):
        return signJWT(user_dict["email"])
    return {"error": "Wrong login details!"}
