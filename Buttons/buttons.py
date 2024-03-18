from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup
from DATABASE import pgdatabase
from MEATHODS import operations


USER_MESSAGE = "Here are some actions you can perform."
USER_BUTTONS = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("Attendance", callback_data="attendance"),InlineKeyboardButton("Bunk", callback_data="bunk")],
        [InlineKeyboardButton("Biometric", callback_data="biometric"),InlineKeyboardButton("Logout", callback_data="logout")],
        [InlineKeyboardButton("Saved Username", callback_data="saved_username")]

    ]
)

yes_no_keyboard = InlineKeyboardMarkup(
inline_keyboard=[
    [InlineKeyboardButton("Remove",callback_data="remove_saved_cred")]
])

ADMIN_OPERATIONS_TEXT = "Menu (ADMIN)"
ADMIN_MESSAGE = f"welcome back!, You have access to additional commands. Here are some actions you can perform."
ADMIN_BUTTONS = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("REQUESTS", callback_data="requests"), InlineKeyboardButton("USERS", callback_data="users")],
        [InlineKeyboardButton("DATABASE", callback_data="database")]
    ]
)

async def start_user_buttons(bot,message):
    await message.reply_text(USER_MESSAGE,reply_markup = USER_BUTTONS)

async def start_admin_buttons(bot,message):
    await message.reply_text(ADMIN_MESSAGE,reply_markup = ADMIN_BUTTONS)



async def callback_function(bot,callback_query):
    if callback_query.data == "attendance":
        _message = callback_query.message
        await operations.attendance(bot,_message)
        await callback_query.answer()
        await callback_query.message.delete()
    elif callback_query.data == "bunk":
        _message = callback_query.message
        await operations.bunk(bot,_message)
        await callback_query.answer()
        await callback_query.message.delete()
    elif callback_query.data == "biometric":
        _message = callback_query.message
        await operations.biometric(bot,_message)
        await callback_query.answer()
        await callback_query.message.delete()
    elif callback_query.data == "logout":
        _message = callback_query.message
        await operations.logout(bot,_message)
        await callback_query.answer()
    elif callback_query.data == "saved_username":
        SAVED_USERNAME_TEXT = "Here are your saved credentials."
        _message = callback_query.message
        USERNAME = await pgdatabase.get_username(chat_id=_message.chat.id)
        SAVED_USERNAME_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= [
                [InlineKeyboardButton(f"{USERNAME}",callback_data="username_saved_options")],
                [InlineKeyboardButton("Back",callback_data="user_back")]
            ]
        )
        await callback_query.edit_message_text(
            SAVED_USERNAME_TEXT,
            reply_markup = SAVED_USERNAME_BUTTONS
        )
    elif callback_query.data == "user_back":
        await callback_query.edit_message_text(USER_MESSAGE,reply_markup = USER_BUTTONS)
    elif callback_query.data == "username_saved_options":
        USERNAME_SAVED_OPTIONS_TEXT = "Here are some operations that you can perform."
        USERNAME_SAVED_OPTIONS_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Remove",callback_data="remove_saved_cred")],
                [InlineKeyboardButton("Remove and Logout", callback_data="remove_logout_saved_cred")],
                [InlineKeyboardButton("Back",callback_data="saved_username")]
            ]
        )
        await callback_query.edit_message_text(
            USERNAME_SAVED_OPTIONS_TEXT,
            reply_markup = USERNAME_SAVED_OPTIONS_BUTTONS
        )
    elif callback_query.data == "remove_saved_cred":
        await callback_query.answer()
        _message = callback_query.message
        chat_id = _message.chat.id
        await pgdatabase.remove_saved_credentials(bot,chat_id)
    elif callback_query.data == "remove_logout_saved_cred":        
        _message = callback_query.message
        chat_id = _message.chat.id
        await pgdatabase.remove_saved_credentials(bot,chat_id)
        await operations.logout(bot,_message)
        await callback_query.answer()
    elif callback_query.data == "requests":
        REQUESTS_TEXT = "Here are some operations that you can perform on requests."
        REQUESTS_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Show Requests",callback_data="show_requests")],
                [InlineKeyboardButton("Clear Requests",callback_data="clear_requests")],
                [InlineKeyboardButton("Back",callback_data="back_to_admin_operations")]
            ]
        )
        await callback_query.edit_message_text(
            REQUESTS_TEXT,
            reply_markup = REQUESTS_BUTTONS
        )
    elif callback_query.data == "show_requests":
        await callback_query.answer()
        _message = callback_query.message
        await operations.show_requests(bot,_message)
    elif callback_query.data == "clear_requests":
        await callback_query.answer()
        _message = callback_query.message
        await operations.clean_pending_requests(bot,_message)
    elif callback_query.data == "back_to_admin_operations":
        await callback_query.edit_message_text(
            ADMIN_MESSAGE,
            reply_markup = ADMIN_BUTTONS
        )
    elif callback_query.data == "users":
        USERS_TEXT = "Here are some operations that you can perform."
        USERS_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Total user (Past 24 hrs)", callback_data="total_users")],
                [InlineKeyboardButton("List of users(QR)",callback_data="list_of_users")],
                [InlineKeyboardButton("Back",callback_data="back_to_admin_operations")],
            ]
        )
        await callback_query.edit_message_text(
            USERS_TEXT,
            reply_markup = USERS_BUTTONS
        )
    elif callback_query.data == "total_users":
        await callback_query.answer()
        _message = callback_query.message
        await operations.total_users(bot,_message)
    elif callback_query.data == "list_of_users":
        await callback_query.answer()
        _message = callback_query.message
        chat_id = _message.chat.id
        await operations.list_users(bot,chat_id)
    elif callback_query.data == "database":
        DATABASE_TEXT = "Select the database that you want to interact with."
        DATABASE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("SQLite3",callback_data="sqlite3")],
                [InlineKeyboardButton("PostgresSQL",callback_data="postgres_sql")],
                [InlineKeyboardButton("Back",callback_data="back_to_admin_operations")]
            ]
        )
        await callback_query.edit_message_text(
            DATABASE_TEXT,
            reply_markup = DATABASE_BUTTONS
        )
    elif callback_query.data == "sqlite3":
        SQLITE3_TEXT = "Here are few SQLITE3 operations."
        SQLITE3_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("RESET",callback_data="reset")],
                [InlineKeyboardButton("Back",callback_data="database")]
            ]
        )
        await callback_query.edit_message_text(
            SQLITE3_TEXT,
            reply_markup =  SQLITE3_BUTTONS
        )
    elif callback_query.data == "reset":
        await callback_query.answer()
        _message = callback_query.message
        await operations.reset_database(bot,_message)
    
    elif callback_query.data == "postgres_sql":
        POSTGRES_TEXT = "Here are few postgres operations."
        POSTGRES_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Total users",callback_data="pgtusers")],
                [InlineKeyboardButton("Back",callback_data="database")]
            ]
        )
        await callback_query.edit_message_text(
            POSTGRES_TEXT,
            reply_markup = POSTGRES_BUTTONS
        )
    elif callback_query.data == "pgtusers":
        await callback_query.answer()
        _message = callback_query.message
        chat_id = _message.chat.id
        await pgdatabase.total_users_pg_database(bot,chat_id)



        