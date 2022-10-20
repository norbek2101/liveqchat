## LiveQChat project


## Project Map

### Root App     -->  ./core
### Rest API     -->  ./api
### WebSocket    -->  ./liveqchat
### SlaveBots    -->  ./bot
### Main Bot     -->  ./main_bot.py
### Secret Keys  -->  ./.env


## Create Environment
```bash
python3 -m venv env
```

## Activate Environment on Linux
```bash
source env/bin/activate
```

## Activate Environment on Windows
```bash
env\Scripts\activate
```

## Execute DataBase
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

## Create Super User
```bash
python manage.py createsuperuser
```

## Run Project (WebSocket & API & SlaveBots)
```bash
python manage.py runserver
```

## Run Main Bot
```bash
python main_bot.py
```
