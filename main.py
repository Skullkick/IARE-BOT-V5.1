from pyrogram import Client, filters
import asyncio,os
from DATABASE import tdatabase,pgdatabase
from METHODS import operations
from Buttons import buttons

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_DEVELOPER_CHAT_ID_re = os.environ.get("DEVELOPER_CHAT_ID")
BOT_MAINTAINER_CHAT_ID_re = os.environ.get("MAINTAINER_CHAT_ID")
bot = Client(
        "IARE BOT",
        bot_token = BOT_TOKEN,
        api_id = API_ID,
        api_hash = API_HASH
)

#Bot Devoloper ID
BOT_DEVELOPER_CHAT_ID = int(BOT_DEVELOPER_CHAT_ID_re)
#Bot Maintainer ID
BOT_MAINTAINER_CHAT_ID = int(BOT_MAINTAINER_CHAT_ID_re)

@bot.on_message(filters.command(commands=['start']))
async def _start(bot,message):
    await operations.get_random_greeting(bot,message)

@bot.on_message(filters.command(commands=['login']))
async def _login(bot,message):
    await operations.login(bot,message)
@bot.on_message(filters.command(commands=['logout']))
async def _logout(bot,message):
    await operations.logout(bot,message)
# @bot.on_message(filters.command(commands=['attendance']))
async def _attendance(bot,message):
    await operations.attendance(bot,message)
    await buttons.start_user_buttons(bot,message)
# @bot.on_message(filters.command(commands=['biometric']))
async def _biometric(bot,message):
    await operations.biometric(bot,message)
    await buttons.start_user_buttons(bot,message)
# @bot.on_message(filters.command(commands=['bunk']))
async def _bunk(bot,message):
    await operations.bunk(bot,message)
    await buttons.start_user_buttons(bot,message)
@bot.on_message(filters.command(commands=['request']))
async def _request(bot,message):
    await operations.request(bot,message)
@bot.on_message(filters.command(commands=['reply']))
async def _reply(bot,message):
    await operations.reply_to_user(bot,message)
@bot.on_message(filters.command(commands=['rshow']))
async def _show_requests(bot,message):
    await operations.show_requests(bot,message)

@bot.on_message(filters.command(commands=['lusers']))
async def _users_list(bot,message):
    await operations.list_users(bot,message.chat.id)
@bot.on_message(filters.command(commands=['tusers']))
async def _total_users(bot,message):
    await operations.total_users(bot,message)
@bot.on_message(filters.command(commands=['rclear']))
async def _clear_requests(bot,message):
    await operations.clean_pending_requests(bot,message)
@bot.on_message(filters.command(commands=['help']))
async def _help(bot,message):
    await operations.help_command(bot,message)
@bot.on_message(filters.command(commands=['reset']))
async def _reset_sqlite(bot,message):
    await operations.reset_database(bot,message)
# @bot.on_message(filters.command(commands=['del_save']))
async def delete_login_details_pgdatabase(bot,message):
    chat_id = message.chat.id
    await pgdatabase.remove_saved_credentials(bot,chat_id)

# @bot.on_message(filters.command(commands=["pgtusers"]))
async def _total_users_pg_database(bot,message):
    chat_id = message.chat.id
    await pgdatabase.total_users_pg_database(bot,chat_id)
@bot.on_message(filters.command(commands="admin"))
async def admin_buttons(bot,message):
    chat_id = message.chat.id
    if chat_id != BOT_DEVELOPER_CHAT_ID and chat_id != BOT_MAINTAINER_CHAT_ID:
        return
    await buttons.start_admin_buttons(bot,message)
@bot.on_callback_query()
async def _callback_function(bot,callback_query):
    await buttons.callback_function(bot,callback_query)


async def main():
    await tdatabase.create_tables()
    await tdatabase.create_total_users_table()
    await tdatabase.create_requests_table()
    await pgdatabase.create_postgres_table()
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    bot.run()