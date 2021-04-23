import motor.motor_asyncio
import config
from bson.objectid import ObjectId

MONGO_DETAILS = "mongodb://{}:{}".format(config.MONGO_HOST, config.MONGO_PORT)

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.TelegramBotManager

users_col = database.get_collection("users_collection")
users_col.create_index("email", unique=True)
bots_col = database.get_collection("bots_collection")
bots_col.create_index("bot_token", unique=True)


def user_normalize(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "password": user["password"]
    }


def bot_normalize(bot) -> dict:
    return {
        "id": str(bot["_id"]),
        "bot_token": bot["bot_token"],
        "userID": bot["userID"]
    }


async def add_user(user_data: dict) -> dict:
    user = await users_col.insert_one(user_data)
    new_user = await users_col.find_one({"_id": user.inserted_id})
    return user_normalize(new_user)


async def retrieve_user(id: str) -> dict:
    user = await users_col.find_one({"_id": ObjectId(id)})
    if user:
        return user_normalize(user)


async def retrieve_user_by_data(email: str, password: str) -> dict:
    user = await users_col.find_one({"email": email, "password": password})
    if user:
        return user_normalize(user)


async def add_bot_db(bot_data: dict) -> dict:
    bot = await bots_col.insert_one(bot_data)
    new_bot = await bots_col.find_one({"_id": bot.inserted_id})
    return bot_normalize(new_bot)


async def delete_bot_db(id: str):
    bot = await bots_col.find_one({"_id": ObjectId(id)})
    if bot:
        await bots_col.delete_one({"_id": ObjectId(id)})
        return True


async def all_user_bots(id: str) -> list:
    bots = []
    async for bot in bots_col.find({"userID": id}):
        bots.append(bot_normalize(bot))
    return bots
