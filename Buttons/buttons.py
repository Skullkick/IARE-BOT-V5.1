from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup
from DATABASE import pgdatabase,tdatabase
from METHODS import operations,labs_driver,labs_handler
import main
import json,asyncio


USER_MESSAGE = "Here are some actions you can perform."
USER_BUTTONS = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("Attendance", callback_data="attendance"),InlineKeyboardButton("Bunk", callback_data="bunk")],
        [InlineKeyboardButton("Biometric", callback_data="biometric"),InlineKeyboardButton("Logout", callback_data="logout")],
        [InlineKeyboardButton("Lab Upload",callback_data="lab_upload_start")],
        [InlineKeyboardButton("Saved Username", callback_data="saved_username")]

    ]
)

remove_cred_keyboard = InlineKeyboardMarkup(
inline_keyboard=[
    [InlineKeyboardButton("Remove",callback_data="remove_saved_cred")]
])

ADMIN_OPERATIONS_TEXT = "Menu (ADMIN)"
ADMIN_MESSAGE = f"welcome back!, You have access to additional commands. Here are some actions you can perform."
ADMIN_BUTTONS = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("REQUESTS", callback_data="requests"), InlineKeyboardButton("USERS", callback_data="users")],
        [InlineKeyboardButton("LOGS",callback_data="log_file")],
        [InlineKeyboardButton("DATABASE", callback_data="database")]
    ]
)

# START_LAB_UPLOAD_MESSAGE = "Here are some operations that you can perform."
# START_LAB_UPLOAD_BUTTONS = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [InlineKeyboardButton("Send PDF ",callback_data="upload_pdf"),InlineKeyboardButton("Title", callback_data="send_title")],
#         [InlineKeyboardButton("Upload Lab Record", callback_data="lab_upload")],
#         [InlineKeyboardButton("Back",callback_data="user_back")]
#     ]
# )

START_LAB_UPLOAD_MESSAGE = f"""
**STEP - 1**
```How to Submit Your Experiment Title
● Title: Title of Experiment.

● Example:
 
Title: Intro to Python.```


**STEP - 2**
```How to Send the PDF file
● You Can Either Forward or Send Your PDF File

● Wait until The Whole Process of Receiving the PDF File completes.```

**STEP - 3**
```Upload Lab PDF
After completing Step 1 and 2,
Click the upload lab record button to upload the PDF.```
"""
START_LAB_UPLOAD_BUTTONS = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("Upload Lab Record", callback_data="lab_upload")],
        [InlineKeyboardButton("Back",callback_data="user_back")]
    ]
)

BACK_TO_USER_BUTTON = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("Back",callback_data="user_back")]
    ]
)
NO_SAVED_LOGIN_TEXT = f"""
```NO SAVED LOGIN
This can be used only by Saved login users.

⫸ How To Save the Login Credentials:

● Click on Logout

● Login Again Using /login username password

● Example : /login 22951A0000 password
```
"""

UPLOAD_PDF_TEXT = "Please send me the PDF file you'd like to upload."
SEND_TITLE_TEXT = f"""
```Send Title
⫸ How To Send Title:

Title : Title of Experiment

⫸ Example:

Title : Introduction to Python

``` 
"""


# Message that needs to be sent if title is not Stored
NO_TITLE_MESSAGE = f"""
```NO TITLE FOUND
⫸ How To Send Title:

Title : Title of Experiment

⫸ Example:

Title : Introduction to Python

``` 
"""

# Message to confirm or change the title
async def start_user_buttons(bot,message):
    await message.reply_text(USER_MESSAGE,reply_markup = USER_BUTTONS)

async def start_admin_buttons(bot,message):
    await message.reply_text(ADMIN_MESSAGE,reply_markup = ADMIN_BUTTONS)

async def remove_title_button(bot,message):
    await message.reply_text()

async def callback_function(bot,callback_query):
    if callback_query.data == "attendance":
        message = callback_query.message
        chat_id = message.chat.id
        
        # Check if the user is a PAT student
        if await operations.check_pat_student(bot, message) is True:
            # Display PAT options
            PAT_BUTTONS = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("PAT Attendance", callback_data="pat_attendance")],
                    [InlineKeyboardButton("Attendance", callback_data="attendance_in_pat_button")],
                    [InlineKeyboardButton("Back", callback_data="user_back")]
                ]
            )
            await callback_query.edit_message_text(USER_MESSAGE, reply_markup=PAT_BUTTONS)
        else:
            # proceed with regular attendance
            await operations.attendance(bot, message)
            await callback_query.answer()
            await message.delete()
            
    elif callback_query.data == "attendance_in_pat_button":
        _message = callback_query.message
        await operations.attendance(bot,_message)  
        await callback_query.answer()  
        await callback_query.message.delete()
    elif callback_query.data == "pat_attendance":
        _message = callback_query.message
        await operations.pat_attendance(bot,_message)
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
        _message = callback_query.message
        USERNAME = await pgdatabase.get_username(chat_id=_message.chat.id)
        if USERNAME is not None:
            SAVED_USERNAME_TEXT = "Here are your saved credentials."

            USERNAME = USERNAME.upper()
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
        else:
            await callback_query.answer()
            await callback_query.edit_message_text(NO_SAVED_LOGIN_TEXT,reply_markup = BACK_TO_USER_BUTTON)
    elif callback_query.data == "lab_upload_start":
        _message = callback_query.message
        chat_id = _message.chat.id
        chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
        if chat_id_in_pgdatabase is False:
            await bot.send_message(chat_id,"This feature is currently available to Saved Credential users")
            await callback_query.answer()
            return
        await tdatabase.store_pdf_status(chat_id,"Recieve")
        await tdatabase.store_title_status(chat_id,"Recieve")
        await callback_query.edit_message_text(START_LAB_UPLOAD_MESSAGE,reply_markup = START_LAB_UPLOAD_BUTTONS)

    elif callback_query.data == "lab_upload":
        _message = callback_query.message
        chat_id = _message.chat.id
        await callback_query.message.delete()
        
        # The amount of time it should check whether the pdf is downloaded or not
        timeout,count = 10,0
        CHECK_FILE = await labs_handler.check_recieved_pdf_file(bot,chat_id)
        while not CHECK_FILE[0]:
        # Sleep briefly before checking again
            if timeout != count:
                count += 2
                await asyncio.sleep(1)
            else:
                await bot.send_message(chat_id,"Unable to find the pdf file. Please try sending the pdf file again.")
                await start_user_buttons(bot,_message)
                return
        # Checks it the title is present or not.
        if await tdatabase.fetch_title_lab_info(chat_id) is None:
            await bot.send_message(chat_id,NO_TITLE_MESSAGE)
            await start_user_buttons(bot,_message)
            return
        # Checks whether if there is any labdata in the database and if not present then it retrieves and stores in database
        if await tdatabase.fetch_lab_subjects_from_lab_info(chat_id) is None and await tdatabase.fetch_lab_weeks_from_lab_info(chat_id) is None:
            await bot.send_message(chat_id,"Please wait while I retrieve the lab details. Fetching lab details from Samvidha.")
            await labs_driver.get_lab_details(bot,chat_id)
        # Fetch the subjects from the sqlite3 database
        lab_details = await tdatabase.fetch_lab_subjects_from_lab_info(chat_id)
        # Deserialize the lab_details data
        lab_details = json.loads(lab_details[0])
        LAB_SUBJECT_TEXT = "Select the subject that you want to upload"
        # Generate InlineKeyboardButtons for lab subjects selection
        LAB_SUBJECT_BUTTONS = [
            [InlineKeyboardButton(lab, callback_data=f"subject_{index + 1}")]
            for index, lab in enumerate(lab_details)
        ]
        LAB_SUBJECT_BUTTONS.append([InlineKeyboardButton("Back", callback_data="user_back")])

        LAB_SUBJECT_BUTTONS_MARKUP = InlineKeyboardMarkup(LAB_SUBJECT_BUTTONS)

        await bot.send_message(
            chat_id,
            text=LAB_SUBJECT_TEXT,
            reply_markup=LAB_SUBJECT_BUTTONS_MARKUP
        )
    elif "subject_" in callback_query.data:
        _message = callback_query.message
        chat_id = _message.chat.id
        selected_subject = callback_query.data.split("subject_")[1]
        # Store selected Subject index in the labuploads database
        await tdatabase.store_subject_index(chat_id,selected_subject)
        # Fetches previously stored data from the database
        week_details = await tdatabase.fetch_lab_weeks_from_lab_info(chat_id)
        # Deserializing the data from database
        week_details = json.loads(week_details[0])
        LAB_WEEK_TEXT = "Select the week"
        LAB_WEEK_BUTTONS = [
            [InlineKeyboardButton(week,callback_data=f"Week-{index}")]
            for index, week in enumerate(week_details)
        ]

        LAB_WEEK_BUTTONS.append([InlineKeyboardButton("Back",callback_data="lab_upload")])
        LAB_WEEK_BUTTONS_MARKUP = InlineKeyboardMarkup(LAB_WEEK_BUTTONS)
        await callback_query.message.edit_text(
                    LAB_WEEK_TEXT,
                    reply_markup=LAB_WEEK_BUTTONS_MARKUP
                )
    elif "Week-" in callback_query.data:
        _message = callback_query.message
        chat_id = _message.chat.id
        selected_week = callback_query.data.split("Week-")[1]
        # Store the index of selected week in database
        await tdatabase.store_week_index(chat_id,selected_week)
        await callback_query.message.delete()
        if await tdatabase.fetch_title_lab_info(chat_id):
            await labs_driver.upload_lab_pdf(bot,_message)
    

    elif callback_query.data == "user_back":
        await callback_query.edit_message_text(USER_MESSAGE,reply_markup = USER_BUTTONS)
    elif callback_query.data == "username_saved_options":
        USERNAME_SAVED_OPTIONS_TEXT = "Here are some operations that you can perform."
        USERNAME_SAVED_OPTIONS_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Remove",callback_data="remove_saved_cred")],
                [InlineKeyboardButton("Remove and Logout", callback_data="remove_logout_saved_cred")],
                [InlineKeyboardButton("Back",callback_data="user_back")]
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
        await tdatabase.delete_lab_upload_data(chat_id) # Deletes the saved Subjects and weeks from database
        await pgdatabase.remove_saved_credentials(bot,chat_id)

    elif callback_query.data == "remove_logout_saved_cred":        
        _message = callback_query.message
        chat_id = _message.chat.id
        await tdatabase.delete_lab_upload_data(chat_id)# Deletes the saved Subjects and weeks from database
        await pgdatabase.remove_saved_credentials(bot,chat_id)
        await operations.logout_user_and_remove(bot,_message)
        await callback_query.answer()

    elif callback_query.data == "log_file":
        _message = callback_query.message
        chat_id = _message.chat.id
        await callback_query.answer()
        await operations.get_logs(bot,chat_id)
        
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
                [InlineKeyboardButton("Total users",callback_data="pgtusers")],
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
                [InlineKeyboardButton("Reset",callback_data="pg_reset")],
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
    elif callback_query.data == "pg_reset":
        _message = callback_query.message
        chat_id = _message.chat.id
        await pgdatabase.clear_database()
        await callback_query.answer()



        
