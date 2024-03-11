# IARE BOT

Telegram Bot which scrapes the data from the [SAMVIDHA](https://samvidha.iare.ac.in/index) and Sends the calculated Attendance, Bunk..etc.

## Environment Variables

- `API_ID` - Get this from [my.telegram.org](https://my.telegram.org/auth).
- `API_HASH` - Get this from [my.telegram.org](https://my.telegram.org/auth).
- `BOT_TOKEN` - Get this from [@BotFather](https://t.me/BotFather).
- `DEVELOPER_CHAT_ID` - Get this from [@RawDataBot](https://t.me/raw_data_bot)
- `MAINTAINER_CHAT_ID` - Get this from [@RawDataBot](https://t.me/raw_data_bot)

## DEPLOY TO HEROKU

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Sathvik2005/IARE-BOT-V5)


## LOCAL DEPLOY
1. Clone the repository.
   ```
   git clone https://github.com/Sathvik2005/IARE-BOT-V5
   ```
2. Enter the directory.
   ```
   cd IARE-BOT-V5
   ```
3. Install all requirements using pip.
   ```
   pip3 install -r requirements.txt
   ```
4. Run the file
   ```
   python3 main.py
   ```
## Available commands:
-    '/login {username} {password}' - Log in with your credentials.

-    '/attendance' - View your attendance details.

-    '/biometric' - View your biometric details.

-    '/bunk' - View the number of classes you can bunk.

-    '/logout' - Log out from the current session.

-    '/request {your request}' - Send a request to the bot developer.

-    Note: Replace {username}, {password}, and {your request} with actual values.
   



