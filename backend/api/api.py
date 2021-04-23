from fastapi import FastAPI, Depends
import json

import config
from backend.auth.auth_handler import signJWT, decodeJWT
from backend.auth.auth_bearer import JWTBearer
import telebot
from threading import Thread

app = FastAPI()
users = []
secret_data = "I am very secret data for the testing"
bots = {}
RealBots = {}


def check_user(data: dict) -> bool:
    for user in users:
        if user["email"] == data["email"] and user["password"] == data["password"]:
            return True
    return False


def start_bot(bot):
    bot.polling(none_stop=True, interval=0)


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
    if len(bots[email]["bots"]) == config.MAX_BOTS_NUMBER:
        return {"error": "You already have max number of bots: {}".format(config.MAX_BOTS_NUMBER)}
    else:
        if bot_token in [bot["token"] for bot in bots[email]["bots"]]:
            return {"error": "You already have a bot with such token"}
        else:
            try:
                bot = telebot.TeleBot(bot_token)
                RealBots[bots[email]["ID"] + 1] = bot

                @bot.message_handler(content_types=['text'])
                def get_text_messages(message):
                    bot.send_message(message.from_user.id, message.text)

                bot_thread = Thread(target=start_bot, args=(bot,), daemon=True)
                bot_thread.start()
            except:
                return {"error": "Cannot create a bot"}
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
            RealBots[bot_id].stop_bot()
            RealBots[bot_id] = None
            return {"message": "bot {} was successfully deleted from your list".format(bot_id)}
    return {"error": "bot with such ID does not exist"}

