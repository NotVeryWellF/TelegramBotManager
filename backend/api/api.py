import time

from fastapi import FastAPI, Depends, Body
from fastapi.encoders import jsonable_encoder
import json
import config
from backend.auth.auth_handler import signJWT, decodeJWT
from backend.auth.auth_bearer import JWTBearer
import telebot
from threading import Thread

from backend.database.database import (
    add_user,
    retrieve_user,
    add_bot_db,
    delete_bot_db,
    all_user_bots,
    retrieve_user_by_data,
)

from backend.models import bot, user

app = FastAPI()
secret_data = "I am very secret data for the testing"
RunningBots = {}


def start_bot(bot):
    bot.polling(none_stop=True, interval=0)


async def check_user(user: user.UserSchema = Body(...)) -> dict:
    retrieved_user = await retrieve_user_by_data(user.email, user.password)
    if retrieved_user:
        return retrieved_user


@app.get('/')
async def root():
    return {'message': 'Simple Telegram Bot Manager'}


@app.post('/signup')
async def create_user(user: user.UserSchema = Body(...)):
    user = jsonable_encoder(user)
    new_user = await add_user(user)
    return signJWT(new_user["email"], new_user["id"])


@app.post('/login')
async def login(user: user.UserSchema = Body(...)):
    obtained_user = await check_user(user)
    if obtained_user:
        return signJWT(obtained_user["email"], obtained_user["id"])
    else:
        return {"error": "Wrong login details!"}


@app.get('/secret')
async def secret(auth: JWTBearer() = Depends(JWTBearer())) -> dict:
    print(auth)
    return {"secret": secret_data}


@app.get('/add_bot')
async def add_bot(bot_token: str, auth: JWTBearer() = Depends(JWTBearer())) -> dict:
    print(auth)
    decoded_JWT = decodeJWT(auth)
    # email = decoded_JWT['email']
    userID = decoded_JWT['userID']

    user_bots = await all_user_bots(userID)
    if len(user_bots) == config.MAX_BOTS_NUMBER:
        return {"error": "You already have max number of bots: {}".format(config.MAX_BOTS_NUMBER)}
    else:
        if bot_token in [bot["bot_token"] for bot in user_bots]:
            return {"error": "You already have a bot with such token"}
        else:
            try:
                bot = telebot.TeleBot(bot_token)

                @bot.message_handler(content_types=['text'])
                def get_text_messages(message):
                    bot.send_message(message.from_user.id, message.text)

                bot_thread = Thread(target=start_bot, args=(bot,), daemon=True)
                bot_thread.start()
            except:
                return {"error": "Cannot create a bot"}

            new_bot = await add_bot_db({"bot_token": bot_token, "userID": userID})
            RunningBots[new_bot['id']] = bot
            return {"message": "Bot was successfully added!"}


@app.get('/get_bot_list')
async def bot_list(auth: JWTBearer() = Depends(JWTBearer())) -> dict:
    email = decodeJWT(auth)["email"]
    userID = decodeJWT(auth)["userID"]
    user_bots = await all_user_bots(userID)
    return {"bots": user_bots}


@app.delete('/delete_bot')
async def delete_bot(bot_id: str, auth: JWTBearer() = Depends(JWTBearer())) -> dict:
    email = decodeJWT(auth)["email"]
    userID = decodeJWT(auth)["userID"]
    user_bots = await all_user_bots(userID)
    for i in user_bots:
        if i["id"] == bot_id:
            deleted_bot = await delete_bot_db(bot_id)
            if deleted_bot:
                RunningBots[bot_id].stop_bot()
                RunningBots[bot_id] = None
                return {"message": "bot {} was successfully deleted from your list".format(bot_id)}
            else:
                return {"error": "Cannot delete bot"}
    return {"error": "bot with such ID does not exist"}

