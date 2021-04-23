from fastapi import FastAPI, Depends
import json
from backend.auth.auth_handler import signJWT, decodeJWT
from backend.auth.auth_bearer import JWTBearer

app = FastAPI()
users = []
secret_data = "I am very secret data for the testing"
bots = {}
max_number_of_bots = 5


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
    users.append(user_dict)
    bots[user_dict["email"]] = {"ID": 0, "bots": []}
    return signJWT(user_dict["email"])


@app.post('/login')
async def login(user: str):
    user_dict = json.loads(user)
    if check_user(user_dict):
        return signJWT(user_dict["email"])
    return {"error": "Wrong login details!"}


@app.get('/secret')
async def secret(auth: JWTBearer() = Depends(JWTBearer())) -> dict:
    email = decodeJWT(auth)["email"]
    print(email)
    return {"secret": secret_data}


@app.post('/add_bot')
async def add_bot(bot_token: str, auth: JWTBearer() = Depends(JWTBearer())) -> dict:
    email = decodeJWT(auth)["email"]
    if len(bots[email]["bots"]) == max_number_of_bots:
        return {"error": "You already have max number of bots: {}".format(max_number_of_bots)}
    else:
        if bot_token in [bot["token"] for bot in bots[email]["bots"]]:
            return {"error": "You already have a bot with such token"}
        else:
            bots[email]["bots"].append({"token": bot_token, "ID": bots[email]["ID"] + 1})
            bots[email]["ID"] += 1
            return {"message": "Bot was successfully added!"}


@app.get('/get_bot_list')
async def bot_list(auth: JWTBearer() = Depends(JWTBearer())) -> dict:
    email = decodeJWT(auth)["email"]
    return {"bots": bots[email]}


@app.delete('/delete_bot')
async def delete_bot(bot_id: int, auth: JWTBearer() = Depends(JWTBearer())) -> dict:
    email = decodeJWT(auth)["email"]
    for i in bots[email]["bots"]:
        if i["ID"] == bot_id:
            bots[email]["bots"].remove(i)
            return {"message": "bot {} was successfully deleted from your list".format(bot_id)}
    return {"error": "bot with such ID does not exist"}