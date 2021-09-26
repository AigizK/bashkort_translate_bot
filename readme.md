**This bot is designed to build up parallel texts.**
We provide users with pre-prepared versions of the text in two languages, and they choose whether the translation is correct or not.

We prepare the proposals in advance using the following tools:
https://github.com/averkij/lingtrain-aligner
https://github.com/averkij/a-studio

In order to start, you need to create a telegram app and bot and get API_ID,HASH,Token . 
This values must be added to the ./config.py

**Sample config.py**

```python
BOT_TOKEN = 'bot token'
API_ID = 00000 # your app id
API_HASH = 'your app hash'
SUPER_ADMIN = "your account id" # super admin can send messges for other users
```

App_ID and hash you can get from https://my.telegram.org/auth
Bot_Token you can get from @BotFather

Also you should fill your DB. I use for it /app/init_db.py

For running you can call:
```shell
python -m app  
```