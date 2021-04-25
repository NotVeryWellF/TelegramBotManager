# Telegram Bot Manager

##  Бэкенд сервиса для управления ботами в Telegram

### Спецификация:
- Сервер работает на простом uvicorn
- API написана на FastAPI
- Авторизация сделана с использованием JWT
- Хранение данных на MongoDB (пароль для пользователя хранится plaintext'ом, можно потом хеширование добавить)
- Заглушка для телеграм ботов работает через python telegram bot API,
для каждого нового добавленного бота просто создается отдельный поток, 
  бот отвечает на полученное сообщение тем же сообщением, при удалении бота поток останавливается
  
### Возможности
- Создать пользователя по уникальному email и паролю
- Залогиниться по данным существующего пользователя
- Добавить бота к юзеру (Не больше максимального количества, указанного в конфиге)
- Удаление бота по его ID
- Получение списка ботов пользователя

### Как поднять
1. На вашем сервере или на другом хосте поднять Mongo\
Инструкция для установки на Ubuntu:
> https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu-tarball/
2. Скачать файлы сервера и установить requirements
> git clone "https://github.com/NotVeryWellF/TelegramBotManager.git" \
> cd `path_to_repo` \
> python3 -m venv venv \
> source venv/bin/activate \
> pip install -r requirements.txt
3. Сконфигурировать данные сервера \
  Открыть `config.yml` файл конфигурации
   
    В поле `api_server`:
   - поставить нужный хост в поле `host` (например: 0.0.0.0)
   - поставить нужный порт в поле `port` (например: 80)
   - поставить максимальное количество ботов на пользователя в поле `max_number_of_bots` (например: 5)
     
    В поле `jwt`:
   - поставить безопасный `secret`
   - поставить время, после которого JWT токен перестанет быть действительным
  
   В поле `mongo`:
   - поставить хост MongoDB сервера в поле `host` (например: 0.0.0.0, если локально)
   - поставить порт MongoDB сервера в поле `port` (например: 27017)
  
4. Запустить сервер
> python3 server.py

### Документация API
1. Документация по API на SwaggerHub:
> https://app.swaggerhub.com/apis-docs/NotVeryWellF/TelegramBotManager/0.1.0

Ну и на `/docs` будет, как подниму где-нибудь на Heroku

2. Примеры использования

#### Создание пользователя (`/signup`)
Представляет собой POST запрос с телом:
>{ \
>  "email": "`some_email@email.email`", \
>  "password": "`some_password`" \
>}

Важно: \
email должен быть в реальном формате email, а то будет ошибка

CURL из `/docs`:
>curl -X 'POST' \ \
  'http://0.0.0.0:8080/signup' \ \
  -H 'accept: application/json' \ \
  -H 'Content-Type: application/json' \ \
  -d '{ \
  "email": "`some_email@email.email`", \
  "password": "`some_password`" \
}'

Если логин уже есть в базе данных, то будет ошибка

Ответом будет Ваш Токен для авторизации и сообщение, что пользователь был успешно добавлен:

Формат ответа:
> { \
  "data": { \
    "access_token": "`your_authorization_token`" \
  }, \
  "code": 200, \
  "message": "Some message for you" \
}


#### Вход по логину и паролю (`/login`)
Представляет собой POST запрос с телом:
>{ \
>  "email": "`some_email@email.email`", \
>  "password": "`some_password`" \
>}

CURL из `/docs`:
> curl -X 'POST' \ \
  'http://0.0.0.0:8080/login' \ \
  -H 'accept: application/json' \ \
  -H 'Content-Type: application/json' \ \
  -d '{ \
  "email": "`some_email@email.email`", \
  "password": "`some_password`" \
}'

Если логин и пароль есть в базе данных, то вам вернется токен для авторизации:

Формат ответа:

>{ \
  "data": { \
    "access_token": "`your_authorization_token`" \
  }, \
  "code": 200, \
  "message": "Some message for you" \
}


> После авторизации и получения токена Вы можете использовать API полноценно
#### Добавление бота (`/add_bot`)
Позволяет пользователю добавить бота к его списку (не больше сконфигурированного максимума) и запускает заглушку на новом боте

Представляет собой POST запрос c одним единственным параметром: \
`bot_token` - токен бота из BotFather

CURL из `/docs`:
> curl -X 'POST' \ \
  'http://0.0.0.0:8080/add_bot?bot_token= `your_bot_token`' \ \
  -H 'accept: application/json' \ \
  -H 'Authorization: Bearer `your_authorization_token`' \ \
  -d ''

Если такого бота еще нет в базе данных и токен бота валидный, то он добавляется и запускается заглушка

Ответом идет простой ответ об успешном добавлении бота

#### Посмотреть список ботов (`/get_bot_list`)
Позволяет получить список всех ботов пользователя

Представляет собой GET запрос без всяких параметров, просто нужно быть авторизированным

CURL из `/docs`:
> curl -X 'GET' \
  'http://0.0.0.0:8080/get_bot_list' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer `your_authorization_token`'

Формат ответа:
>{ \
  "data": [ \
    { \
      "id": "bot id", \
      "bot_token": "bot token", \
      "userID": "Your user id" \
    }, \
    { \
      "id": "another bot id", \
      "bot_token": "bot token", \
      "userID": "Your user id" \
    } \
  ], \
  "code": 200, \
  "message": "Some message for you" \
}

#### Удаление бота (`/delete_bot`)
Позволяет удалить бота пользователя из списка

Представляет собой DELETE запрос c одним параметром: \
`bot_id` - ID бота из базы данных (его можно получить из списка ботов пользователя)

CURL из `/docs`:
> curl -X 'DELETE' \
  'http://0.0.0.0:8080/delete_bot?bot_id= `your_bot_id`' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer `your_authorization_token`'

Ответом идет простой ответ об успешном удалении бота

