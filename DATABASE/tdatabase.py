# This file is used to store userdata temporarily in local storage
# Current server restarts every 24hrs So all the data present in the databases will be lost
import sqlite3, json
import os

DATABASE_FILE = "user_sessions.db"

TOTAL_USERS_DATABASE_FILE = "total_users.db"

REQUESTS_DATABASE_FILE = "requests.db"

LAB_UPLOAD_DATABASE_FILE = "labuploads.db"

async def create_user_sessions_tables():
    """
    Create the necessary tables in the SQLite database.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        # Create a table to store user sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                chat_id INTEGER PRIMARY KEY,
                session_data TEXT,
                user_id TEXT
            )
        """)
        conn.commit()
#The usernames accessed this bot
async def create_total_users_table():
    """
    Create the total_users table in the SQLite database.
    """
    with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE
            )
        """)
        conn.commit()

async def create_requests_table():
    with sqlite3.connect(REQUESTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pendingreq(
                       unique_id TEXT PRIMARY KEY,
                       user_id TEXT,
                       message TEXT,
                       chat_id INTEGER
            )
        """)
        conn.commit()

async def create_lab_upload_table():
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lab_upload_info (
                chat_id TEXT PRIMARY KEY,
                title TEXT,
                subject_index INTEGER,
                week_index INTEGER,
                subjects TEXT,
                weeks TEXT,
                pdf_status TEXT,
                title_status TEXT
            )
        """)
        conn.commit()


async def fetch_usernames_total_users_db():
    with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users")
        usernames = [row[0] for row in cursor.fetchall()]
    return usernames

async def fetch_number_of_total_users_db():
    with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_count = cursor.fetchone()[0]
    return total_count
        

async def store_user_session(chat_id, session_data, user_id):
    """
    Store the user session data in the SQLite database.

    Parameters:
        chat_id (int): The chat ID of the user.
        session_data (str): JSON-formatted string containing the session data.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO sessions (chat_id, session_data, user_id) VALUES (?, ?, ?)",
                       (chat_id, session_data, user_id))
        
        conn.commit()

async def store_username(username):
    """
    Store a username in the total_users table.

    Parameters:
        username (str): The username to store.
    """
    with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)",
                       (username,))
        conn.commit()

async def load_user_session(chat_id):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT session_data FROM sessions WHERE chat_id=?", (chat_id,))
        result = cursor.fetchone()
        if result:
            session_data = json.loads(result[0])
            # Check if the session data contains the 'username'
            if 'username' in session_data:
                return session_data
            else:
                return None

async def load_username(chat_id):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE chat_id=?", (chat_id,))
        row = cursor.fetchone()
        return row

async def store_lab_info(chat_id,subject_index,week_index,subjects,weeks):
    """Store lab information in the database.
    
    :param chat_id: Chat ID of the user.
    :param subject_index: Selected subject index.
    :param week_index: Selected week index.
    :param subjects: List of subjects.
    :param weeks: List of weeks.
    """
    
    subjects = json.dumps(subjects) # Serializing the data so that it can be stored.
    weeks = json.dumps(weeks)
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            if subject_index is not None:
                cursor.execute('UPDATE lab_upload_info SET subject_index = ? WHERE chat_id = ?', (subject_index, chat_id))
            if week_index is not None:
                cursor.execute('UPDATE lab_upload_info SET week_index = ? WHERE chat_id = ?', (week_index, chat_id))
            if weeks is not None:
                cursor.execute('UPDATE lab_upload_info SET weeks = ? WHERE chat_id = ?', (weeks, chat_id))
            if subjects is not None:
                cursor.execute('UPDATE lab_upload_info SET subjects = ? WHERE chat_id = ?', (subjects, chat_id))
        else:
            cursor.execute('INSERT INTO lab_upload_info (chat_id, subject_index, week_index, subjects, weeks) VALUES (?, ?, ?, ?, ?)',
                        (chat_id, subject_index, week_index,subjects,weeks))

        conn.commit()

async def store_subject_index(chat_id,subject_index):
    """This function is used to store the subject_index in the database to retrieve later

    :param chat_id: chat_id of the user based on the message received from the user.
    :param subject_index: Selected week_index is stored in the database"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET subject_index = ? WHERE chat_id = ?', (subject_index, chat_id))
        conn.commit()

async def store_week_index(chat_id,week_index):
    """This function is used to store the week_index in the database to retrieve later

    :param chat_id: chat_id of the user based on the message received from the user.
    :param week_index: Selected week_index is stored in the database"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET week_index = ? WHERE chat_id = ?', (week_index, chat_id))
        conn.commit()

async def store_title(chat_id,title):
    """This function is used to store the title in the database to use later

    :param chat_id: chat_id of the user based on the message received from the user.
    :param title: Title is stored in the database"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET title = ? WHERE chat_id = ?', (title, chat_id))
        else:
            cursor.execute('INSERT INTO lab_upload_info (chat_id, title) VALUES (?, ?)',
            (chat_id, title))
        conn.commit()

async def store_pdf_status(chat_id,status):
    """This function is used to store the pdf status

    :param chat_id: chat_id of the user based on the message received from the user.
    :param status: Status that needs to be stored (We are storing status as "Receiving")"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET pdf_status = ? WHERE chat_id = ?', (status, chat_id))
        else:
            cursor.execute('INSERT INTO lab_upload_info (chat_id, pdf_status) VALUES (?, ?)',
            (chat_id, status))
        conn.commit()

async def store_title_status(chat_id,status):
    """This function is used to store the title status

    :param chat_id: chat_id of the user based on the message received from the user
    :param status: status that needs to be stored (we are storing status as "Receiving")"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET title_status = ? WHERE chat_id = ?', (status, chat_id))
        else:
            cursor.execute('INSERT INTO lab_upload_info (chat_id, title_status) VALUES (?, ?)',
            (chat_id, status))
        conn.commit()

async def fetch_lab_subjects_from_lab_info(chat_id):
    """This function is used to fetch all the labs data from the database

    :param chat_id: chat_id of the user based on the message.
    :return: returns the data of labs."""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT subjects FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        all_labs_subjects = cursor.fetchone()
        if all_labs_subjects is None:
            return None
        elif all_labs_subjects[0] is not None:
            return all_labs_subjects

async def fetch_lab_weeks_from_lab_info(chat_id):
    """This function is used to fetch all the weeks data from the database

    :param chat_id: chat_id of the user based on the message.
    :return: returns the data of weeks."""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT weeks FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        all_lab_weeks = cursor.fetchone()
        if all_lab_weeks is None:
            return None
        elif all_labs_weeks[0] is not None:
            return all_lab_weeks

async def fetch_indexes_and_title_lab_info(chat_id):
    """This function is used to fetch the title,subject_index,week_index from the database

    :param chat_id: chat_id of the user based on the messagee."""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT title,subject_index, week_index FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        lab_info = cursor.fetchone()
        return lab_info

async def  fetch_title_lab_info(chat_id):
    """This Function is sued to fetch the title from the lab_upload_info

    :param chat_id: The chat_id of the user
    :return: title_info"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT title FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        title_info = cursor.fetchone()
        return title_info
    
async def fetch_pdf_status(chat_id):
    """This Function is used to get the status of the pdf, This is necessary for receiving the pdf from the user

    :param chat_id: chat_id of the user based on message.
    :return: pdf_status"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT pdf_status FROM lab_upload_info WHERE chat_id = ?',(chat_id,))
        pdf_status = cursor.fetchone()
        return pdf_status

async def fetch_title_status(chat_id):
    """This Function is used to get the status of the title, This is necessary for receiving the title from the user

    :param chat_id: chat_id of the user based on message.
    :return: title_status"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT title_status FROM lab_upload_info WHERE chat_id = ?',(chat_id,))
        title_status = cursor.fetchone()
        return title_status

async def delete_title_status_info(chat_id):
    """This function removes the status of the title from the database

    :param chat_id: chat_id of the user based on the message received."""

    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET title_status = ? WHERE chat_id = ?', (None, chat_id))
            return True
        else:
            return False
async def delete_pdf_status_info(chat_id):
    """This Function is used to remove the pdf status of a specified user in the database
    
    :param chat_id: chat_id of the user
    :return: Boolean"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET pdf_status = ? WHERE chat_id = ?', (None, chat_id))
            return True
        else:
            return False


async def delete_indexes_and_title_info(chat_id):
    """This function deletes the selected index values and the title information stored in the database
    :param chat_id: chat_id of the user"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET title = ?, subject_index = ?, week_index = ? WHERE chat_id = ?', (None,None,None, chat_id))
            conn.commit()
            return True
async def delete_user_session(chat_id):
    """
    Delete the user session data from the SQLite database.

    Parameters:
        chat_id (int): The chat ID of the user.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE chat_id=?", (chat_id,))
        conn.commit()

async def clear_sessions_table():
    """
    Clear all rows from the sessions table.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions")
        conn.commit()

async def store_requests(unique_id, user_id, message, chat_id):
    """This function is used to store the requests sent by the user"""
    with sqlite3.connect(REQUESTS_DATABASE_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO pendingreq (unique_id, user_id, message, chat_id) VALUES (?, ?, ?, ?)",
                  (unique_id, user_id, message, chat_id))
        conn.commit()

async def load_requests(unique_id):
    """This Function can be used to get a request info based on unique_id"""
    with sqlite3.connect(REQUESTS_DATABASE_FILE ) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pendingreq WHERE unique_id=?",(unique_id,))
        row = cursor.fetchone()
        return row
    
async def load_allrequests():
    """This function is used to get all the  requests present in the database
    returns all requests"""
    with sqlite3.connect(REQUESTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pendingreq")
        all_messages = cursor.fetchall()
        return all_messages

async def delete_lab_upload_data(chat_id):
    """This function is used to delete the row of a user based on chat_id in lab_upload_info table"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lab_upload_info WHERE chat_id=?",(chat_id,))
        conn.commit()

async def delete_request(unique_id):
    """This Function deletes the request based on unique_id"""
    with sqlite3.connect(REQUESTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pendingreq WHERE unique_id=?",(unique_id,))
        conn.commit()
async def clear_requests():
    """This function is used to clear all the requests in the requests database"""
    with sqlite3.connect(REQUESTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pendingreq")
        conn.commit()


