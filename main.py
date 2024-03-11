from pyrogram import Client, filters
from bs4 import BeautifulSoup 
from pytz import timezone
from datetime import datetime, timedelta
import random, requests,json,asyncio, uuid, sqlite3, pyqrcode, os
from DATABASE import tdatabase


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

async def get_indian_time():
    return datetime.now(timezone('Asia/Kolkata'))
@bot.on_message(filters.command('start'))
async def get_random_greeting(bot,message):
    """
    Get a random greeting based on the time and day.
    """
    indian_time = await get_indian_time()
    current_hour = indian_time.hour
    current_weekday = indian_time.weekday()

    morning_greetings = ["Good morning!", "Hello, early bird!", "Rise and shine!", "Morning!"]
    afternoon_greetings = ["Good afternoon!", "Hello there!", "Afternoon vibes!", "Hey!"]
    evening_greetings = ["Good evening!", "Hello, night owl!", "Evening time!", "Hi there!"]

    weekday_greetings = ["Have a productive day!", "Stay focused and have a great day!", "Wishing you a wonderful day!", "Make the most of your day!"]
    weekend_greetings = ["Enjoy your weekend!", "Relax and have a great weekend!", "Wishing you a fantastic weekend!", "Make the most of your weekend!"]

    if 5 <= current_hour < 12:  # Morning (5 AM to 11:59 AM)
        greeting = random.choice(morning_greetings)
    elif 12 <= current_hour < 18:  # Afternoon (12 PM to 5:59 PM)
        greeting = random.choice(afternoon_greetings)
    else:  # Evening (6 PM to 4:59 AM)
        greeting = random.choice(evening_greetings)

    if 0 <= current_weekday < 5:  # Monday to Friday
        greeting += " " + random.choice(weekday_greetings)
    else:  # Saturday and Sunday
        greeting += " " + random.choice(weekend_greetings)

    await message.reply(greeting)
async def perform_login(chat_id, username, password):
    """
    Perform login with the provided username and password.

    Returns:
        bool: True if login is successful, False otherwise.
    """
    # Set up the necessary headers and cookies
    cookies = {'PHPSESSID': ''}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://samvidha.iare.ac.in',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://samvidha.iare.ac.in/index',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }

    data = {
        'username': username,
        'password': password,
    }

    with requests.Session() as s:
        index_url = "https://samvidha.iare.ac.in/index"
        login_url = "https://samvidha.iare.ac.in/pages/login/checkUser.php"
        home_url = "https://samvidha.iare.ac.in/home"

        response = s.get(index_url)
        cookie_to_extract = 'PHPSESSID'
        cookie_value = response.cookies.get(cookie_to_extract)
        cookies['PHPSESSID'] = cookie_value

        s.post(login_url, cookies=cookies, headers=headers, data=data)

        response = s.get(home_url)
        if '<title>IARE - Dashboard - Student</title>' in response.text:

            session_data = {
                'cookies': s.cookies.get_dict(),
                'headers': headers,
                'username': username  # Save the username in the session data
            }
            return session_data
        else:   
            return None
        
# async def is_user_logged_in(user_id):
#     return user_id in user_sessions

@bot.on_message(filters.command('login'))
async def login(bot,message):
    chat_id = message.chat.id
    # command_args = message.get_args().split()
    command_args = message.text.split()[1:]
    # if await is_user_logged_in(chat_id):  # Implement is_user_logged_in function
    if await tdatabase.load_user_session(chat_id):
        await message.reply("You are already logged in.")
        return

    if len(command_args) != 2:
        await message.reply("Invalid command format. Use /login {username} {password}.")
        return

    username = command_args[0]
    password = command_args[1]

    # Perform login
    session_data = await perform_login(chat_id, username, password)  # Implement perform_login function

    if session_data:
        await tdatabase.store_user_session(chat_id, json.dumps(session_data), username)  # Implement store_user_session function

        await tdatabase.store_username(username)
        await message.delete()
        await bot.send_message(chat_id,text="Login successful!")
    else:
        await bot.send_message(chat_id,text="Invalid username or password.")


@bot.on_message(filters.command('logout'))
async def logout(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)

    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        await bot.send_message(chat_id,text="Please log in using the /login command.")
        return

    logout_url = 'https://samvidha.iare.ac.in/logout'
    session_data = await tdatabase.load_user_session(chat_id)
    cookies,headers = session_data['cookies'], session_data['headers']
    requests.get(logout_url, cookies=cookies, headers=headers)
    await tdatabase.delete_user_session(chat_id)

    await message.reply("Logout successful.")

async def logout_user(bot,chat_id):
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        return

    await tdatabase.delete_user_session(chat_id)

    await bot.send_message(chat_id, text="Your session has been logged out due to inactivity.")

@bot.on_message(filters.command('attendance'))
async def attendance(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        await bot.send_message(chat_id,"Please log in using the /login command.")
        return

    # Access the attendance page and retrieve the content
    attendance_url = 'https://samvidha.iare.ac.in/home?action=stud_att_STD'
    
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)

        attendance_response = s.get(attendance_url)

    data = BeautifulSoup(attendance_response.text, 'html.parser')
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in attendance_response.text:
        await logout_user(bot,chat_id)
        return
    table_all = data.find_all('table', class_='table table-striped table-bordered table-hover table-head-fixed responsive')
    if len(table_all) > 1:
        req_table = table_all[1]

        table_data = []

        rows = req_table.tbody.find_all('tr')

        for row in rows:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            table_data.append(row_data)
        sum_attendance = 0
        count_att = 0
        for row in table_data[0:]:
            course_name = row[2]
            conducted = row[5]
            attended = row[6]
            attendance_percentage = row[7]
            attendance_status = row[8]
            if course_name and attendance_percentage:
                att_msg = f"""
```{course_name}

● Conducted         -  {conducted}
             
● Attended          -  {attended}  
         
● Attendance %      -  {attendance_percentage} 
            
● Status            -  {attendance_status}  
         
```
"""
                # att_msg = f"Course: {course_name}, Attendance: {attendance_percentage}"
                sum_attendance += float(attendance_percentage)
                if float(attendance_percentage) > 0:
                        count_att += 1
                await bot.send_message(chat_id,att_msg)
        aver_attendance = round(sum_attendance/count_att, 2)
        over_all_attendance = f"**Overall Attendance is {aver_attendance}**"
        await bot.send_message(chat_id,over_all_attendance)

    else:
        await bot.send_message(chat_id,"Attendance data not found.")


@bot.on_message(filters.command('biometric'))
async def biometric(_,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        await bot.send_message(chat_id,"Please log in using the /login command.")
        return

    biometric_url = 'https://samvidha.iare.ac.in/home?action=std_bio'
    with requests.Session() as s:

        cookies = session_data['cookies']
        s.cookies.update(cookies)
        headers = session_data['headers']

        response = s.get(biometric_url, headers=headers)

        biodata = BeautifulSoup(response.text, 'html.parser')
    biotable = biodata.find('tbody')
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in response.text:
        await logout_user(bot,chat_id)
        return
    if not biotable:
        await message.reply("Biometric data not found.")
        return
    days_present = 0
    days_absent = 0
    total_days = 0

    biorows = biotable.find_all('tr')
    for row in biorows:
        cells = row.find_all('td')
        status = cells[9].get_text(strip=True)
        if 'Present' in status:
            days_present += 1
        elif 'Absent' in status:
            days_absent += 1
    total_days = days_present + days_absent
        # total_days += 1

    biometric_percentage = (days_present / total_days) * 100 if total_days != 0 else 0
    biometric_percentage = round(biometric_percentage,3)
    #biometric_msg = f"Number of Days Present: {days_present}\nNumber of Days Absent: {days_absent}\nTotal Number of Days: {total_days}\nBiometric Percentage: \n{biometric_percentage}%"
    intimes = []
    outtimes = []
    time_gap_more_than_six_hours = 0
    sixintime = []
    sixoutime = []
    for row in biorows:
        cell = row.find_all('td')
        intime = cell[7].text.strip()
        outtime = cell[8].text.strip()
        if intime and outtime and ':' in intime and ':' in outtime:
            intimes.append(intime)
            outtimes.append(outtime)
            intime_hour, intime_minute = intime.split(':')
            outtime_hour, outtime_minute = outtime.split(':')
            time_difference = (int(outtime_hour) - int(intime_hour)) * 60 + (int(outtime_minute) - int(intime_minute))
            if time_difference >= 360:
                time_gap_more_than_six_hours += 1
        sixintime.append(intime)
        sixoutime.append(outtime)
    six_percentage = (time_gap_more_than_six_hours / total_days) * 100 if total_days != 0 else 0
    six_percentage = round(six_percentage, 3)
    #biometric_msg += f"\nbiometric Percentage(6 hours gap):\n{six_percentage}%"
    next_biometric_time_str = None
    if sixintime and sixintime[0] :
        next_biometric_time = datetime.strptime(sixintime[0], "%H:%M") + timedelta(hours=6)
        next_biometric_time_str = next_biometric_time.strftime("%H:%M")
        #biometric_msg += f"\nBiometric should be kept again at: {next_biometric_time_str}"
    if next_biometric_time_str==None:
        biometric_msg = f"""
    ```Biometric
⫷

● Total Days             -  {total_days}
                
● Days Present           -  {days_present}  
            
● Days Absent            -  {days_absent}
                
● Biometric %            -  {biometric_percentage}  
            
● Biometric % (6h gap)   -  {six_percentage}

⫸

@iare_unofficial_bot
    ```
    """
    else:
        biometric_msg = f"""
    ```Biometric
⫷

● Total Days             -  {total_days}
                
● Days Present           -  {days_present}  
            
● Days Absent            -  {days_absent}
                
● Biometric %            -  {biometric_percentage}  
            
● Biometric % (6h gap)   -  {six_percentage}

● Evening Biometric Time  -  {next_biometric_time_str}

⫸

@iare_unofficial_bot
    ```
    """
    await bot.send_message(chat_id,text=biometric_msg)

@bot.on_message(filters.command(commands=['bunk']))
async def bunk(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        await message.reply("Please log in using the /login command.")
        return

    attendance_url = 'https://samvidha.iare.ac.in/home?action=stud_att_STD'
    
    with requests.Session() as s:

        cookies = session_data['cookies']
        s.cookies.update(cookies)

        attendance_response = s.get(attendance_url)

    data = BeautifulSoup(attendance_response.text, 'html.parser')
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in attendance_response.text:
        await logout_user(bot,chat_id)
        return

    table_all = data.find_all('table', class_='table table-striped table-bordered table-hover table-head-fixed responsive')
    if len(table_all) > 1:

        req_table = table_all[1]
        table_data = []
        rows = req_table.tbody.find_all('tr')
        for row in rows:
            cells = row.find_all('td')

            row_data = [cell.get_text(strip=True) for cell in cells]

            table_data.append(row_data)

        for row in table_data[0:]:
            course_name = row[2]
            attendance_percentage = row[7]
            if course_name and attendance_percentage:
                attendance_present = float(attendance_percentage)
                attendance_threshold = 75
                total_classes = int(row[5])
                attended_classes = int(row[6])
                classes_bunked = 0
                
                if attendance_present >= attendance_threshold:
                    classes_bunked = 0
                    while (attended_classes / (total_classes + classes_bunked)) * 100 >= attendance_threshold:
                        classes_bunked += 1

                    # bunk_can_msg = f"{course_name}: {attendance_percentage}% (Can bunk {classes_bunked} classes)"
                    #await bot.send_message(chat_id,bunk_can_msg)
                    classes_bunked -= 1
                    bunk_can_msg = f"""
```{course_name}
⫷

● Attendance  -  {attendance_percentage}

● You can bunk {classes_bunked} classes

⫸

```
"""

                    await bot.send_message(chat_id,bunk_can_msg)
                  
                    
                else:
                    classes_needattend = 0
                    while((attended_classes + classes_needattend) / (total_classes + classes_needattend)) * 100 < attendance_threshold:
                        classes_needattend += 1
                    # bunk_cannot_msg = f"{course_name}:Attendance below 75%"
                    # bunk_recover_msg = f"{course_name}: Attend {classes_needattend} classes for 75%"
                    # await bot.send_message(chat_id,bunk_cannot_msg)
                    
                    bunk_recover_msg = f"""
```{course_name}
⫷

● Attendance  -  Below 75%

● Attend  {classes_needattend} classes for 75%

● No Bunk Allowed

⫸

```
"""
                    await bot.send_message(chat_id,bunk_recover_msg)
              
    else:
        await message.reply("Data not found.")

async def generate_unique_id():
    """
    Generate a unique identifier using UUID version 4.

    Returns:
        str: A string representation of the UUID.
    """
    return str(uuid.uuid4())

@bot.on_message(filters.command(commands=['request']))
async def request(bot,message):
    chat_id = message.from_user.id

    # Check if the user is logged in
    # if not is_user_logged_in(user_id):
    if not await tdatabase.load_user_session(chat_id):
        await message.reply("Please log in using the /login command.")
        return

    user_request = " ".join(message.text.split()[1:])
    if not user_request:
        await message.reply("Request cannot be empty.")
        return
    getuname = await tdatabase.load_username(chat_id)

    username = getuname[3]

    user_unique_id = await generate_unique_id()

    await tdatabase.store_requests(user_unique_id,username,user_request,chat_id)

    forwarded_message = f"New User Request from @{username} (ID: {user_unique_id}):\n\n{user_request}"
    await bot.send_message(BOT_DEVELOPER_CHAT_ID,text=forwarded_message)

    await bot.send_message(chat_id,"Thank you for your request! Your message has been forwarded to the developer.")


@bot.on_message(filters.command(commands=['reply']))
async def reply_to_user(_,message):

    if message.chat.id != BOT_DEVELOPER_CHAT_ID and message.chat.id != BOT_MAINTAINER_CHAT_ID:
        return

    if not message.reply_to_message:
        await message.reply("Please reply to a user's request to send a reply.")
        return


    reply_text = message.reply_to_message.text
    unique_id_keyword = "ID: "
    if unique_id_keyword not in reply_text:
        await message.reply("The replied message does not contain the unique ID.")
        return


    unique_id_start_index = reply_text.find(unique_id_keyword) + len(unique_id_keyword)
    unique_id_end_index = reply_text.find(")", unique_id_start_index)
    request_id = reply_text[unique_id_start_index:unique_id_end_index].strip()
    pending_requests = await tdatabase.load_requests(request_id)

    if request_id not in pending_requests:
        await message.reply("Invalid or unknown unique ID.")
        return


    user_chat_id = pending_requests[3]

    developer_reply = message.text.split("/reply", 1)[1].strip()

    reply_message = f"{developer_reply}\n\nThis is a reply from the bot developer."

    try:

        await bot.send_message(chat_id=user_chat_id, text=reply_message)


        developer_chat_id = message.chat.id
        await bot.send_message(chat_id=developer_chat_id, text="Message sent successfully.")

        await tdatabase.delete_request(request_id)
    except Exception as e:
        error_message = f"An error occurred while sending the message to the user: {e}"
        await bot.send_message(chat_id=developer_chat_id, text=error_message)

@bot.on_message(filters.command(commands=['rshow']))
async def rshow(bot,message):
    chat_id = message.from_user.id
    requests = await tdatabase.load_allrequests()
    if message.chat.id != BOT_DEVELOPER_CHAT_ID and message.chat.id != BOT_MAINTAINER_CHAT_ID:
        return

    if len(requests) == 0:
        await bot.send_message(chat_id,text="There are no pending requests.")
        return
    for request in requests:
        unique_id, user_id, message, chat_id = request
        request_message = f"New User Request from user ID {user_id} (Unique ID: {unique_id}):\n\n{message}"
        await bot.send_message(chat_id, text=request_message)

@bot.on_message(filters.command(commands=['lusers']))
async def list_users(bot,message):
    if message.from_user.id == BOT_DEVELOPER_CHAT_ID or message.chat.id==BOT_MAINTAINER_CHAT_ID:
        with sqlite3.connect(tdatabase.TOTAL_USERS_DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users")
            usernames = [row[0] for row in cursor.fetchall()]
            
            users_list = ";".join(usernames)
            qr_code = pyqrcode.create(users_list)
            qr_image_path = "list_users_qr.png"
            qr_code.png(qr_image_path, scale=5)
            await bot.send_photo(message.chat.id, photo=open(qr_image_path, 'rb'))

            os.remove(qr_image_path)

@bot.on_message(filters.command(commands=['tusers']))
async def total_users(_,message):
    if message.from_user.id == BOT_DEVELOPER_CHAT_ID or message.chat.id==BOT_MAINTAINER_CHAT_ID:
        with sqlite3.connect(tdatabase.TOTAL_USERS_DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total_count = cursor.fetchone()[0]
            await bot.send_message(message.chat.id,f"Total users: {total_count}")

@bot.on_message(filters.command(commands=['rclear']))
async def clean_pending_requests(bot,message):
    if message.chat.id == BOT_DEVELOPER_CHAT_ID or message.chat.id == BOT_MAINTAINER_CHAT_ID:
        await tdatabase.clear_requests()
        await bot.send_message(BOT_DEVELOPER_CHAT_ID,"Emptied the requests successfully")

@bot.on_message(filters.command(commands=['help']))
async def help_command(bot,message):
    """
    Handler function for the /help command.
    Provides information about the available commands.
    """
    chat_id = message.chat.id
    help_msg = """Available commands:

    /login username password - Log in with your credentials.

    /attendance - View your attendance details.

    /biometric - View your biometric details.

    /bunk - View the number of classes you can bunk.

    /logout - Log out from the current session.

    /request {your request} - Send a request to the bot devoloper.

    Note: Replace {username}, {password}, and {your request} with actual values.
    """
    help_dmsg = """Available commands:

    /login {username} {password} - Log in with your credentials.

    /attendance - View your attendance details.

    /biometric - View your biometric details.

    /bunk - View the number of classes you can bunk.

    /logout - Log out from the current session.
    
    /request {your request} - Send a request to the bot Developer.

    /reply {your reply} - Send a reply to the request by replying to it.

    /rshow - Show the requests.

    /rclear - Clear the requests.

    /lusers - Show the list of users.

    /tusers - Show the total number of users

    /reset - Reset the Database

    Note: Replace {username}, {password}, {your request} and {your reply} with actual values.
    """
    if chat_id==BOT_DEVELOPER_CHAT_ID or chat_id==BOT_MAINTAINER_CHAT_ID:
        await bot.send_message(chat_id,text=help_dmsg)
    else:
        await bot.send_message(chat_id,text=help_msg)

@bot.on_message(filters.command('reset'))
async def reset_database(bot,message):
    if message.chat.id==BOT_DEVELOPER_CHAT_ID or message.chat.id == BOT_MAINTAINER_CHAT_ID:
        await tdatabase.clear_sessions_table()
        await message.reply("Reset done")
async def main():
    await tdatabase.create_tables()
    await tdatabase.create_total_users_table()
    await tdatabase.create_requests_table()
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    bot.run()