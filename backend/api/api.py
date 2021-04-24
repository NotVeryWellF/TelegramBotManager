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


def generateResponse(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message
    }


def generateError(error, code, message):
    return {"error": error, "code": code, "message": message}


async def check_user(user: user.UserSchema = Body(...)) -> dict:
    retrieved_user = await retrieve_user_by_data(user.email, user.password)
    if retrieved_user:
        return retrieved_user


@app.get('/')
async def root():
    return generateResponse("", "Simple Telegram Bot Manager")


@app.post('/signup')
async def create_user(user: user.UserSchema = Body(...)):
    user = jsonable_encoder(user)
    try:
        new_user = await add_user(user)
    except:
        return generateError("An error occurred", 404, "User already exists, try again")
    return generateResponse(signJWT(new_user["email"], new_user["id"]), "User was successfully added")


@app.post('/login')
async def login(user: user.UserSchema = Body(...)):
    obtained_user = await check_user(user)
    if obtained_user:
        return generateResponse(signJWT(obtained_user["email"], obtained_user["id"]), "You logged in successfully")
    else:
        return generateError("An error occurred", 404, "User with such email and password does not exist")


@app.get('/secret')
async def secret(auth: JWTBearer() = Depends(JWTBearer())) -> dict:
    return generateResponse({"secret": secret_data}, "You successfully got our secret data)))")


@app.get('/add_bot')
async def add_bot(bot_token: str, auth: JWTBearer() = Depends(JWTBearer())) -> dict:
    decoded_JWT = decodeJWT(auth)
    email = decoded_JWT['email']
    userID = decoded_JWT['userID']

    user_bots = await all_user_bots(userID)
    if len(user_bots) == config.MAX_BOTS_NUMBER:
        return generateError("An error occurred",
                             404,
                             "You already have max number of bots: {}".format(config.MAX_BOTS_NUMBER))
    else:
        if bot_token in [bot["bot_token"] for bot in user_bots]:
            return generateError("An error occurred", 404, "You already have a bot with such token")
        else:
            try:
                bot = telebot.TeleBot(bot_token)

                @bot.message_handler(content_types=['text'])
                def get_text_messages(message):
                    bot.send_message(message.from_user.id, message.text)

                bot_thread = Thread(target=start_bot, args=(bot,), daemon=True)
                bot_thread.start()
            except:
                return generateError("An error occurred", 404, "Cannot create a bot")

            try:
                new_bot = await add_bot_db({"bot_token": bot_token, "userID": userID})
            except:
                bot.stop_bot()
                return generateError("An error occurred", 404, "Cannot create a bot")

            RunningBots[new_bot['id']] = bot
            return generateResponse("", "Bot {} was successfully added!".format(new_bot['id']))


@app.get('/get_bot_list')
async def bot_list(auth: JWTBearer() = Depends(JWTBearer())) -> dict:
    email = decodeJWT(auth)["email"]
    userID = decodeJWT(auth)["userID"]
    user_bots = await all_user_bots(userID)
    return generateResponse(user_bots, "All user's bots")


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
                return generateResponse("", "bot {} was successfully deleted from your list".format(bot_id))
            else:
                return generateError("An error occurred", 404, "Cannot delete bot")
    return generateError("An error occurred", 404, "bot with such ID does not exist")

