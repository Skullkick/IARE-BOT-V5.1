# IARE UNOFFICIAL BOT

Telegram Bot which scrapes the data from the [SAMVIDHA](https://samvidha.iare.ac.in/index) and Sends the calculated Attendance, Biometric etc.

## Environment Variables

- `API_ID` - Get this from [my.telegram.org](https://my.telegram.org/auth).
- `API_HASH` - Get this from [my.telegram.org](https://my.telegram.org/auth).
- `BOT_TOKEN` - Get this from [@BotFather](https://t.me/BotFather).
- `DEVELOPER_CHAT_ID` - Get this from [@RawDataBot](https://t.me/raw_data_bot)
- `MAINTAINER_CHAT_ID` - Get this from [@RawDataBot](https://t.me/raw_data_bot)
- `POSTGRES_USER_ID` - Get this From [@Heroku](https://devcenter.heroku.com/articles/heroku-postgresql#connecting-to-heroku-postgres)
- `POSTGRES_PASSWORD` - Get this From [@Heroku](https://devcenter.heroku.com/articles/heroku-postgresql#connecting-to-heroku-postgres)
- `POSTGRES_DATABASE` - Get this From [@Heroku](https://devcenter.heroku.com/articles/heroku-postgresql#connecting-to-heroku-postgres)
- `POSTGRES_HOST` - Get this From [@Heroku](https://devcenter.heroku.com/articles/heroku-postgresql#connecting-to-heroku-postgres)
- `POSTGRES_PORT` - Get this From [@Heroku](https://devcenter.heroku.com/articles/heroku-postgresql#connecting-to-heroku-postgres)

## DEPLOY TO HEROKU

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Skullkick/IARE-BOT-V5.1)


## LOCAL DEPLOY
1. Clone the repository.
   ```
   git clone https://github.com/Skullkick/IARE-BOT-V5.1
   ```
2. Enter the directory.
   ```
   cd IARE-BOT-V5.1
   ```
3. Install all requirements using pip.
   ```
   pip3 install -r requirements.txt
   ```
4. Run the file
   ```
   python3 main.py
   ```
## Available commands for User:
-    '/login {username} {password}' - Log in with your credentials.

-    '/logout' - Log out from the current session.

-    /report {your report} - Send a report to the bot developer.

-    Note: Replace {username}, {password}, and {your request} with actual values.
   
## Available Buttons for User:
-    `Attendance` - View your attendance details.

-    `PAT Attendance` - View your PAT attendance details.

-    `Biometric` - View your biometric details.

-    `Bunk` - View the number of classes you can bunk.

-    `Logout` - Log out from the current session.

-   `Saved Username` - Displays saved Username in Database and allows user to remove saved login or remove saved login and logout.

## Available Commands for Admin
These commands are not accessable for a normal user, Only BOT_DEVELOPER and BOT_MAINTAINER can access these commands.

- '/reply {your reply}' - Send a reply to the request by replying to it.

- '/rshow' - Show the requests.

- '/rclear' - Clear the requests.

- '/lusers' - Show the list of users.

- '/tusers' - Show the total number of users

- '/reset' - Reset the SQllite Database

- '/admin' - Instead of using command initiates buttons.
  
## Available Buttons for Admin

-   `Requests` - Show all the Requests.
  
-   `Users` - `Total Users(Past 24Hrs)` and `List of users(Past 24Hrs)`

-   `DATABASE` - `SQLITE3` Reset the SQlite3 database.
  
-   `DATABASE`  - `POSTGRES` Total users in database and reset the database.
