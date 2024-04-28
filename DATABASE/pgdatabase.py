import asyncpg,os
# Data stored in this database is permanent, only if user removes the data will be removed.

#Database Credentials
USER_CRED = os.environ.get("POSTGRES_USER_ID")
PASSWORD_CRED = os.environ.get("POSTGRES_PASSWORD")
DATABASE_CRED = os.environ.get("POSTGRES_DATABASE")
HOST_CRED = os.environ.get("POSTGRES_HOST")
PORT_CRED = os.environ.get("POSTGRES_PORT")

async def connect_pg_database():
    """connect_pg_database is used to make a connection to the postgres database"""
     # connecting to the PSQL database
    connection = await asyncpg.connect(
        user=USER_CRED,
        password=PASSWORD_CRED,
        database=DATABASE_CRED,
        host=HOST_CRED,
        port=PORT_CRED
    )
    return connection

async def create_postgres_table():  
    """This function is used to create a table in postgres database if it dosent exist"""
    conn = await connect_pg_database() 
    try:
        await conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS user_credentials (
                chat_id BIGINT PRIMARY KEY,
                username VARCHAR(25),
                password VARCHAR(30),
                pat_student BOOLEAN DEFAULT false
            )
            '''
        )
        return True
    except Exception as e:
        print(f"Error creating table: {e}")
        return False
    finally:
        
        await conn.close()



async def check_chat_id_in_pgb(chat_id):
    """This function checks whether the chat_id of the user is already present in the database or not
    and returns true or false values"""
    connection = await connect_pg_database()
    try:
        
        result = await connection.fetchval(
            "SELECT EXISTS (SELECT 1 FROM user_credentials WHERE chat_id = $1)",
            chat_id
        )
        return result
    except Exception as e:
        return False
    finally:
        await connection.close()


async def get_username(chat_id):
    """Retrieve username from the PostgreSQL database"""
    connection = await connect_pg_database()
    try:
        
        result = await connection.fetchval(
            "SELECT username FROM user_credentials WHERE chat_id = $1",
            chat_id
        )
        return result
    except Exception as e:
        print(f"Error retrieving username from database: {e}")
        return None
    finally:
        if connection:
            await connection.close()


async def save_credentials_to_databse(chat_id, username, password):
    """This is used to save the username and password to the pgdatabase"""
    connection = await connect_pg_database() 
    try:
         # Await the coroutine
        await connection.execute(
            "INSERT INTO user_credentials (chat_id, username, password) VALUES ($1, $2, $3)",
            chat_id, username, password
        )
        return True
    except Exception as e:
        print(f"Error saving to database: {e}")
        return False
    finally:
        if connection:
            await connection.close()


async def retrieve_credentials_from_database(chat_id):
    """This Function is used to Retreive the user credentials based on the chat_id
    Returns username and password. Used to login the user automatically during session timeout"""
    connection = await connect_pg_database()
    try:
        
        result = await connection.fetchrow(
            "SELECT username, password FROM user_credentials WHERE chat_id = $1",
            chat_id
        )
        if result:
            return result['username'], result['password']
        else:
            return None, None
    except Exception as e:
        print(f"Error retrieving credentials from database: {e}")
        return None, None
    finally:
        if connection:
            await connection.close()

async def remove_saved_credentials(bot,chat_id):
    """This Function removes the Column based on chat_id. 
    This is used to remove the saved credentials."""
    connection = await connect_pg_database()
    try:
        
        await connection.execute("DELETE FROM user_credentials WHERE chat_id = $1", chat_id)
        
        await bot.send_message(chat_id,"Data deleted successfully!")
    
    except Exception as e:
        await bot.send_message(chat_id,f"Error deleting data: {e}")
    
    finally:
        
        await connection.close()

async def clear_database():
    """This Function Clears the Postgres database."""
    # Connecting to the PSQL database
    connection = await connect_pg_database()
    try:
        async with connection.transaction():
            # Execute the SQL command to delete data
            await connection.execute("DELETE FROM user_credentials")

        print("Data erased successfully!")
        return True
    except Exception as e:
        print(f"Error clearing database: {e}")
        return False
    finally:
        # Close the database connection
        await connection.close()

async def total_users_pg_database(bot,chat_id):
    """This Function return the Total Number of users in the database."""
    connection = await connect_pg_database()
    try:
        query = "SELECT COUNT(*) FROM user_credentials"
        result = await connection.fetchval(query)
        await bot.send_message(chat_id, f"Total users in the Postgres database: {result}")
    except Exception as e:
        await bot.send_message(chat_id, f"Error retrieving data: {e}")
    finally:
        await connection.close()

async def get_all_chat_ids():
    """This Function Gets all the Chat_ids Present in the database"""
    conn = await connect_pg_database()
    try:
        query = "SELECT chat_id FROM user_credentials"
        result = await conn.fetch(query)
        # Returns the data in list.
        return [record['chat_id'] for record in result]
    except Exception as e:
        print(f"Error fetching chat IDs: {e}")
        return []
    finally:
        await conn.close()

async def get_pat_student(chat_id):
    """This Function checks whether the pat_student column is True or False, Based on chat_id of the user"""
    connection = await connect_pg_database()
    try:
        
        result = await connection.fetchrow(
            "SELECT pat_student FROM user_credentials WHERE chat_id = $1",
            chat_id
        )
        if result:
            return result['pat_student']
        else:
            return False
    except Exception as e:
        print(f"Error retrieving credentials from database: {e}")
        return False
    finally:
        if connection:
            await connection.close()
async def set_pat_student_true(chat_id):
    """This Function Sets the pat_student Colum to True"""
    connection = await connect_pg_database()
    try:
        # Execute UPDATE query to set pat_student to True for the specified user_id
        await connection.execute('''
            UPDATE user_credentials
            SET pat_student = TRUE
            WHERE chat_id = $1
        ''', chat_id)
        return True
    except asyncpg.PostgresError as e:
        print(f"Error setting pat_student to True: {e}")
        return False
    finally:
        await connection.close()