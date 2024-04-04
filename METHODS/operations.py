from DATABASE import tdatabase,pgdatabase
from Buttons import buttons
from bs4 import BeautifulSoup 
import requests,json,uuid,os,pyqrcode,random
from pytz import timezone
from datetime import datetime


BOT_DEVELOPER_CHAT_ID_re = os.environ.get("DEVELOPER_CHAT_ID")
BOT_MAINTAINER_CHAT_ID_re = os.environ.get("MAINTAINER_CHAT_ID")



BOT_DEVELOPER_CHAT_ID = int(BOT_DEVELOPER_CHAT_ID_re)

BOT_MAINTAINER_CHAT_ID = int(BOT_MAINTAINER_CHAT_ID_re)

async def get_indian_time():
    return datetime.now(timezone('Asia/Kolkata'))
async def get_random_greeting(bot,message):
    """
    Get a random greeting based on the time and day.
    """
    chat_id = message.chat.id
    indian_time = await get_indian_time()
    current_hour = indian_time.hour
    current_weekday = indian_time.weekday()

    # List of greetings based on the time of day
    morning_greetings = ["Good morning!", "Hello, early bird!", "Rise and shine!", "Morning!"]
    afternoon_greetings = ["Good afternoon!", "Hello there!", "Afternoon vibes!", "Hey!"]
    evening_greetings = ["Good evening!", "Hello, night owl!", "Evening time!", "Hi there!"]

    # List of greetings based on the day of the week
    weekday_greetings = ["Have a productive day!", "Stay focused and have a great day!", "Wishing you a wonderful day!", "Make the most of your day!"]
    weekend_greetings = ["Enjoy your weekend!", "Relax and have a great weekend!", "Wishing you a fantastic weekend!", "Make the most of your weekend!"]

    # Get a random greeting based on the time of day
    if 5 <= current_hour < 12:  # Morning (5 AM to 11:59 AM)
        greeting = random.choice(morning_greetings)
    elif 12 <= current_hour < 18:  # Afternoon (12 PM to 5:59 PM)
        greeting = random.choice(afternoon_greetings)
    else:  # Evening (6 PM to 4:59 AM)
        greeting = random.choice(evening_greetings)

    # Add a weekday-specific greeting if it's a weekday, otherwise, add a weekend-specific greeting
    if 0 <= current_weekday < 5:  # Monday to Friday
        greeting += " " + random.choice(weekday_greetings)
    else:  # Saturday and Sunday
        greeting += " " + random.choice(weekend_greetings)

    # Send the greeting to the user
    await message.reply(greeting)

    # Check if User Logged-In else,return LOGIN_MESSAGE

    # LOGIN MESSAGE
    login_message = f"""
```NO USER FOUND
⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 22951A0000 iare_unoffical_bot
```
"""
    
    if not await tdatabase.load_user_session(chat_id) and await pgdatabase.check_chat_id_in_pgb(chat_id) is False:
        await bot.send_message(chat_id,login_message)
        
    else:
        await buttons.start_user_buttons(bot,message)


async def is_user_logged_in(bot,message):
    chat_id = message.chat.id
    if await tdatabase.load_user_session(chat_id):
        return True


async def get_username(bot,message):
    user = await bot.get_users(message.from_user.id)
    user_name = f"{user.first_name} {user.last_name}" 
    return user_name

async def perform_login( username, password):
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


async def login(bot,message):
    chat_id = message.chat.id
    command_args = message.text.split()[1:]
    if await tdatabase.load_user_session(chat_id):
        await message.reply("You are already logged in.")
        await buttons.start_user_buttons(bot,message)
        return

    if len(command_args) != 2:
        await message.reply("Invalid command format. Use /login {username} {password}.")
        return

    username = command_args[0]
    password = command_args[1]
    session_data = await perform_login(username, password)

    if session_data:
        await tdatabase.store_user_session(chat_id, json.dumps(session_data), username)
        await tdatabase.store_username(username)
        await message.delete()
        await bot.send_message(chat_id,text="Login successful!")
        if not await pgdatabase.check_chat_id_in_pgb(chat_id):
            save = await pgdatabase.save_credentials_to_databse(chat_id,username,password)
            if save is True:
                await bot.send_message(chat_id,"Your login details have been successfully recorded")
                await message.reply_text("Your password has been saved. If you don't want your password to be saved Click \"Remove\"",reply_markup =buttons.yes_no_keyboard)
            else:
                await bot.send_message(chat_id,"There is an error saving credentials.")

            
            
        else:
            await bot.send_message(chat_id,text="Your login information has already been registered.")
        await buttons.start_user_buttons(bot,message)
        
    else:
        await bot.send_message(chat_id,text="Invalid username or password.")

async def auto_login_by_database(bot,message,chat_id):
    username,password = await pgdatabase.retrieve_credentials_from_database(chat_id)
    session_data = await perform_login(username, password)
    if session_data:
        await tdatabase.store_user_session(chat_id, json.dumps(session_data), username)  # Implement store_user_session function
        await tdatabase.store_username(username)
        await bot.send_message(chat_id,text="Login successful!")
        return True
    else:
        if await pgdatabase.check_chat_id_in_pgb(chat_id) is True:
            await bot.send_message(chat_id,text="Unable to login using saved credentials, please try updating your password")

async def logout(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)

    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        login_message = f"""
```NO USER FOUND
⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 22951A0000 iare_unoffical_bot
```
        """
        await bot.send_message(chat_id,text=login_message)
        return

    logout_url = 'https://samvidha.iare.ac.in/logout'
    session_data = await tdatabase.load_user_session(chat_id)
    cookies,headers = session_data['cookies'], session_data['headers']
    requests.get(logout_url, cookies=cookies, headers=headers)
    await tdatabase.delete_user_session(chat_id)

    await message.reply("Logout successful.")

async def logout_user_and_remove(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)

    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        await bot.send_message(chat_id,text="You are already logged out.")
        return

    logout_url = 'https://samvidha.iare.ac.in/logout'
    session_data = await tdatabase.load_user_session(chat_id)
    cookies,headers = session_data['cookies'], session_data['headers']
    requests.get(logout_url, cookies=cookies, headers=headers)
    await tdatabase.delete_user_session(chat_id)

    await message.reply("Logout successful.")

async def logout_user_if_logged_out(bot,chat_id):
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        return

    await tdatabase.delete_user_session(chat_id)

    await bot.send_message(chat_id, text="Your session has been logged out due to inactivity.")

async def silent_logout_user_if_logged_out(bot,chat_id):
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        return

    await tdatabase.delete_user_session(chat_id)

async def attendance(bot,message):
    chat_id = message.chat.id
    chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        if await auto_login_by_database(bot,message,chat_id) is False and chat_id_in_pgdatabase is False:
            # LOGIN MESSAGE
            
            login_message = f"""
```NO USER FOUND
⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 22951A0000 iare_unoffical_bot

``` 
"""
            
            await bot.send_message(chat_id,login_message)
            return
        else:
            session_data = await tdatabase.load_user_session(chat_id)

    # Access the attendance page and retrieve the content
    attendance_url = 'https://samvidha.iare.ac.in/home?action=stud_att_STD'
    
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)

        attendance_response = s.get(attendance_url)

    data = BeautifulSoup(attendance_response.text, 'html.parser')
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in attendance_response.text:
        if chat_id_in_pgdatabase:
            await silent_logout_user_if_logged_out(bot,chat_id)
            await attendance(bot,message)
        else:
            await logout_user_if_logged_out(bot,chat_id)
        return
    table_all = data.find_all('table', class_='table table-striped table-bordered table-hover table-head-fixed responsive')
    if len(table_all) > 1:
        req_table = table_all[1]

        table_data = []

        rows = req_table.tbody.find_all('tr')
        
        # ATTENDANCE HEADING
        
        attendance_heading = f"""
```ATTENDANCE
@iare_unofficial_bot
```
"""
        await bot.send_message(chat_id,attendance_heading)

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
                if int(conducted) > 0:
                        count_att += 1
                await bot.send_message(chat_id,att_msg)
        aver_attendance = round(sum_attendance/count_att, 2)
        over_all_attendance = f"**Overall Attendance is {aver_attendance}**"
        await bot.send_message(chat_id,over_all_attendance)

    else:
        await bot.send_message(chat_id,"Attendance data not found.")
    await buttons.start_user_buttons(bot,message)
#Biometric
async def biometric(bot, message):
    chat_id = message.chat.id
    chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        if await auto_login_by_database(bot, message, chat_id) is False and not chat_id_in_pgdatabase:
            # LOGIN MESSAGE
            
            login_message = f"""
```NO USER FOUND
⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 22951A0000 iare_unoffical_bot

``` 
"""
            
            await bot.send_message(chat_id,login_message)
            return
        else:
            session_data = await tdatabase.load_user_session(chat_id)

    biometric_url = 'https://samvidha.iare.ac.in/home?action=std_bio'
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        headers = session_data['headers']
        response = s.get(biometric_url, headers=headers)

        # Parse the HTML content using BeautifulSoup
        Biometric_html = BeautifulSoup(response.text, 'html.parser')

    # Check if the response contains the expected title
    if '<title>Samvidha - Campus Management Portal - IARE</title>' in response.text:
        if chat_id_in_pgdatabase:
            await silent_logout_user_if_logged_out(bot, chat_id)
            await biometric(bot, message)
        else:
            await logout_user_if_logged_out(bot, chat_id)
        return

    # Find the table
    biometric_table = Biometric_html.find('table', class_='table')

    if not biometric_table:
        await message.reply("Biometric data not found.")
        return

    # Dictionary to store attendance data for each student
    attendance_data = {
        'Total Days Present': 0,
        'Total Days Absent': 0,
        'Total Days': 0
    }

    # Find all rows in the table body except the last one
    biometric_rows = biometric_table.find('tbody').find_all('tr')[:-1]

    for row in biometric_rows:
        # Extract data from each row
        cells = row.find_all('td')
        status = cells[6].text.strip()
        if status.lower() == 'present':
            attendance_data['Total Days Present'] += 1
        else:
            attendance_data['Total Days Absent'] += 1

    attendance_data['Total Days'] = attendance_data['Total Days Present'] + attendance_data['Total Days Absent']
    # Calculate the biometric percentage
    biometric_percentage = (attendance_data['Total Days Present'] / attendance_data['Total Days']) * 100 if attendance_data['Total Days'] != 0 else 0
    biometric_percentage = round(biometric_percentage, 3)

    # Calculate the biometric percentage with six hours gap
    six_percentage = await six_hours_biometric(biometric_rows, attendance_data['Total Days'])

    biometric_msg = f"""
    ```Biometric
⫷

● Total Days             -  {attendance_data['Total Days']}
                    
● Days Present           -  {attendance_data['Total Days Present']}  
                
● Days Absent            -  {attendance_data['Total Days Absent']}
                    
● Biometric %            -  {biometric_percentage}

● Biometric % (6h gap)   -  {six_percentage}

⫸

@iare_unofficial_bot
    ```
    """
    await bot.send_message(chat_id, biometric_msg)
    
    await buttons.start_user_buttons(bot,message)

async def six_hours_biometric(biometric_rows, totaldays):
    intimes, outtimes = [], []
    time_gap_more_than_six_hours = 0
    for row in biometric_rows:
        cell = row.find_all('td')
        intime = cell[4].text.strip()
        outtime = cell[5].text.strip()
        if intime and outtime and ':' in intime and ':' in outtime:
            intimes.append(intime)
            outtimes.append(outtime)
            intime_hour, intime_minute = intime.split(':')
            outtime_hour, outtime_minute = outtime.split(':')
            time_difference = (int(outtime_hour) - int(intime_hour)) * 60 + (int(outtime_minute) - int(intime_minute))
            if time_difference >= 360:
                time_gap_more_than_six_hours += 1
    # Calculate the biometric percentage with six hours gap
    six_percentage = (time_gap_more_than_six_hours / totaldays) * 100 if totaldays != 0 else 0
    six_percentage = round(six_percentage, 3)
    return six_percentage


async def bunk(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    if not session_data:
        if await auto_login_by_database(bot,message,chat_id) is False and chat_id_in_pgdatabase is False:
            # LOGIN MESSAGE
            
            login_message = f"""
```NO USER FOUND
⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 22951A0000 iare_unoffical_bot

``` 
"""
    
            await bot.send_message(chat_id,login_message)
            return
            
        else:
            session_data = await tdatabase.load_user_session(chat_id)

    attendance_url = 'https://samvidha.iare.ac.in/home?action=stud_att_STD'
    
    with requests.Session() as s:

        cookies = session_data['cookies']
        s.cookies.update(cookies)

        attendance_response = s.get(attendance_url)

    data = BeautifulSoup(attendance_response.text, 'html.parser')
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in attendance_response.text:
        if chat_id_in_pgdatabase:
            await silent_logout_user_if_logged_out(bot,chat_id)
            await bunk(bot,message)
        else:
            await logout_user_if_logged_out(bot,chat_id)
        return

    table_all = data.find_all('table', class_='table table-striped table-bordered table-hover table-head-fixed responsive')
    if len(table_all) > 1:

        req_table = table_all[1]
        table_data = []
        rows = req_table.tbody.find_all('tr')
        
        # BUNK HEADING
    
        bunk_heading = f"""
```BUNK
@iare_unofficial_bot
```
"""
        await bot.send_message(chat_id,bunk_heading)
        
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
                conducted_classes = int(row[5])
                attended_classes = int(row[6])
                classes_bunked = 0
                
                if attendance_present >= attendance_threshold:
                    classes_bunked = 0
                    while (attended_classes / (conducted_classes + classes_bunked)) * 100 >= attendance_threshold:
                        classes_bunked += 1
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
                    if conducted_classes == 0:
                        classes_needattend = 0
                    else:
                        while((attended_classes + classes_needattend) / (conducted_classes + classes_needattend)) * 100 < attendance_threshold:
                            classes_needattend += 1    
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
    await buttons.start_user_buttons(bot,message)

async def generate_unique_id():
    """
    Generate a unique identifier using UUID version 4.

    Returns:
        str: A string representation of the UUID.
    """
    return str(uuid.uuid4())

# CHECKS IF REGISTERED FOR PAT

async def check_pat_student(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    if not session_data:
        if await auto_login_by_database(bot,message,chat_id) is False and chat_id_in_pgdatabase is False:
            login_message = f"""
```NO USER FOUND
⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 22951A0000 iare_unoffical_bot

``` 
"""

            await bot.send_message(chat_id,login_message)
            return
        else:
            session_data = await tdatabase.load_user_session(chat_id)
    pat_attendance_url = "https://samvidha.iare.ac.in/home?action=Attendance_std"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)

        pat_attendance_response = s.get(pat_attendance_url)
    data = BeautifulSoup(pat_attendance_response.text, 'html.parser')
    td_tags = re.findall(r'<td\s*[^>]*>.*?</td>', str(data), flags=re.DOTALL)

    # Count the number of <td> tags found
    num_td_tags = len(td_tags)
    # print("Number of <td> tags:", num_td_tags)

    if(num_td_tags > 2):
        return True
    else:
        return False



# PAT ATTENDENCE IF REGISTERED

async def pat_attendance(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    if not session_data:
        if await auto_login_by_database(bot,message,chat_id) is False and chat_id_in_pgdatabase is False:
            login_message = f"""
```NO USER FOUND
⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 22951A0000 iare_unoffical_bot

``` 
"""
    
            await bot.send_message(chat_id,login_message)
            return
        else:
            session_data = await tdatabase.load_user_session(chat_id)
    pat_attendance_url = "https://samvidha.iare.ac.in/home?action=Attendance_std"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)

        pat_attendance_response = s.get(pat_attendance_url)
        pat_att_heading = f"""
```PAT ATTENDANCE
@iare_unofficial_bot
```
"""
        await bot.send_message(chat_id,pat_att_heading)
    data = BeautifulSoup(pat_attendance_response.text, 'html.parser')
    tables = data.find_all('table')
    for table in tables:
        rows = table.find_all('tr')

        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 7:
                course_name = columns[2].text.strip()
                conducted_classes = columns[3].text.strip()
                attended_classes = columns[4].text.strip()  
                attendance_percentage = columns[5].text.strip()
                att_status = columns[6].text.strip()
                att_msg = f"""
```{course_name}

● Conducted         -  {conducted_classes}
             
● Attended          -  {attended_classes}  
         
● Attendance %      -  {attendance_percentage} 
            
● Status            -  {att_status}  
         
```
"""
                await bot.send_message(chat_id,att_msg)
    await buttons.start_user_buttons(bot,message)

async def request(bot,message):
    chat_id = message.from_user.id
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        if await auto_login_by_database(bot,message,chat_id) is False and await pgdatabase.check_chat_id_in_pgb(chat_id) is False:
            # LOGIN MESSAGE
            login_message = f"""
```NO USER FOUND
⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 22951A0000 iare_unoffical_bot
```
"""
            await bot.send_message(chat_id,login_message)
            return
        else:
            session_data = await tdatabase.load_user_session(chat_id)

    user_request = " ".join(message.text.split()[1:])
    if not user_request:
        await message.reply("Request cannot be empty.")
        return
    getuname = await tdatabase.load_username(chat_id)

    username = getuname[2]

    user_unique_id = await generate_unique_id()

    await tdatabase.store_requests(user_unique_id,username,user_request,chat_id)

    forwarded_message = f"New User Request from @{username} (ID: {user_unique_id}):\n\n{user_request}"
    await bot.send_message(BOT_DEVELOPER_CHAT_ID,text=forwarded_message)

    await bot.send_message(chat_id,"Thank you for your request! Your message has been forwarded to the developer.")

async def reply_to_user(bot,message):

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

async def show_requests(bot,message):
    chat_id = message.chat.id
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

async def list_users(bot,chat_id):
    if chat_id == BOT_DEVELOPER_CHAT_ID or chat_id==BOT_MAINTAINER_CHAT_ID:
        usernames = await tdatabase.fetch_usernames_total_users_db()   
        users_list = ";".join(usernames)
        qr_code = pyqrcode.create(users_list)
        qr_image_path = "list_users_qr.png"
        qr_code.png(qr_image_path, scale=5)
        await bot.send_photo(chat_id, photo=open(qr_image_path, 'rb'))
        os.remove(qr_image_path)

async def total_users(bot,message):
    chat_id = message.chat.id
    if chat_id == BOT_DEVELOPER_CHAT_ID or chat_id ==BOT_MAINTAINER_CHAT_ID:
        total_count = await tdatabase.fetch_number_of_total_users_db()
        await bot.send_message(message.chat.id,f"Total users: {total_count}")

async def clean_pending_requests(bot,message):
    if message.chat.id == BOT_DEVELOPER_CHAT_ID or message.chat.id == BOT_MAINTAINER_CHAT_ID:
        await tdatabase.clear_requests()
        await bot.send_message(BOT_DEVELOPER_CHAT_ID,"Emptied the requests successfully")

async def help_command(bot,message):
    """
    Handler function for the /help command.
    Provides information about the available commands.
    """
    chat_id = message.chat.id
    help_msg = """Available commands:

    /login username password - Log in with your credentials.

    /logout - Log out from the current session.

    /request {your request} - Send a request to the bot devoloper.

    Note: Replace {username}, {password}, and {your request} with actual values.
    """
    help_dmsg = """Available commands:

    /login {username} {password} - Log in with your credentials.
    
    /logout - Log out from the current session.    
    
    /request {your request} - Send a request to the bot Developer.

    /admin - get access to the authorized operations.

    /reply {your reply} - Send a reply to the request by replying to it.

    /reset - Reset the Database

    Note: Replace {username}, {password}, {your request} and {your reply} with actual values.
    """
    if chat_id==BOT_DEVELOPER_CHAT_ID or chat_id==BOT_MAINTAINER_CHAT_ID:
        await bot.send_message(chat_id,text=help_dmsg)
        await buttons.start_user_buttons(bot,message)
    else:
        await bot.send_message(chat_id,text=help_msg)
        if is_user_logged_in(chat_id,message) is True or await pgdatabase.check_chat_id_in_pgb(chat_id):
            await buttons.start_user_buttons(bot,message)

async def reset_database(bot,message):
    if message.chat.id==BOT_DEVELOPER_CHAT_ID or message.chat.id == BOT_MAINTAINER_CHAT_ID:
        await tdatabase.clear_sessions_table()
        await message.reply("Reset done")
