import logging
import time
import os
import json

import selenium.common
from webdriver_manager.chrome import ChromeDriverManager as ChromeDriver

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpecCond

from Buttons import buttons
from DATABASE import pgdatabase
from DATABASE import tdatabase
from METHODS import labs_handler

from bs4 import BeautifulSoup

class HeadlessLabUpload:

    def __init__(self, username: str, password: str) -> None:
        """
        The constructor initializes the username, password, selenium webdriver, and
        logging object. All are attributes of the class.

        :param username: The IARE Username.
        :param password: The Username's Password.
        """

        # Initializing Username And Password.
        self.username = username
        self.password = password

        # Initialing Logging Object
        try:
            logging.basicConfig(
                format="%(asctime)s - %(levelname)s - %(message)s",
                filename="logs.log",
                filemode="a",
                level=logging.INFO
            )
        except Exception as LoggingError:
            print(f"Logging Unavailable For {self.username}, Due To \n{LoggingError}.")

        # Initialing Driver
        try:
            chrome_service_object = Service(executable_path=ChromeDriver().install())

            # Making The Version Headless.
            chrome_options_object = Options()
            chrome_options_object.add_argument("--headless")
            chrome_options_object.add_argument("--disable-gpu")

            self.driver = webdriver.Chrome(options=chrome_options_object, service=chrome_service_object)
        except Exception as DriverError:
            logging.info(f"Driver Creation Unsuccessful For {self.username}.")
            exit(1)
        finally:
            logging.info(f"Driver Creation Successful For {self.username}.")


    def login_to_samvidha(self):
        """
        The function uses the above initialized driver to log in to samvidha. It also returns
        a boolean that represents the same.

        It is utilizing the new WebDriverWait.
        :return: True for successful login, else False.
        """

        login_attempts = 0
        while login_attempts < 5:
            try:
                self.driver.get("https://samvidha.iare.ac.in/")

                # Waiting For Username Element To Pass Keys.
                username_element = WebDriverWait(self.driver, timeout=2).until(
                    ExpecCond.presence_of_element_located((By.ID, "txt_uname"))
                )

                username_element.send_keys(self.username)

                # Waiting For Password Element To Pass Keys.
                password_element = WebDriverWait(self.driver, timeout=2).until(
                    ExpecCond.presence_of_element_located((By.ID, "txt_pwd"))
                )

                password_element.send_keys(self.password)

                # Waiting For Sign-In Button To Click.
                sign_in_element = WebDriverWait(self.driver, timeout=2).until(
                    ExpecCond.presence_of_element_located((By.ID, "but_submit"))
                )

                sign_in_element.click()

                # Waiting For Verification Element To Return Boolean.
                verification_element = WebDriverWait(self.driver, timeout=2).until(
                    ExpecCond.presence_of_element_located((By.CLASS_NAME, "hidden-xs"))
                )

                if "IARE - Dashboard - Student" in self.driver.page_source:
                    if verification_element.text:
                        logging.info(f"Log-In Successful For {self.username}.")
                        return True

            except selenium.common.TimeoutException:
                login_attempts += 1
                logging.info(f"Log-In Failed For {self.username}. Attempts Remaining: {login_attempts}.")

            except Exception as LoginErrors:
                login_attempts += 1
                logging.info(
                    f"Log-In Failed For {self.username}, Due To {LoginErrors}. Attempts Remaining: {login_attempts}.")

        logging.info(f"Log-In Unsuccessful For {self.username}.")
        self.driver.quit()
        return False
    
    def find_lab_upload_url(self):
        """
        This is a simple function that tries 5 times to find lab_upload URL.
        This function can be called only if login_to_samvidha() is successful.

        :return: URL: str, that can be used to get to the lab upload page for that user.
        """
        lab_attempts = 0
        while lab_attempts < 5:
            try:
                # Finding the lab_record element
                lab_record_element = self.driver.find_element(by=By.CSS_SELECTOR, value="[title='Lab Record']")

                # Finding URL
                lab_record_url = lab_record_element.get_attribute("href")

                # Verifying Lab URL.
                if lab_record_url:
                    logging.info(msg=f"Lab Record URL Successfully Found For {self.username}.")
                    return lab_record_url

            # Catching Lab Element Errors And Logging.
            except selenium.common.NoSuchElementException:
                lab_attempts += 1
                logging.info(
                    msg=f"Could Not Find Lab Upload URL For {self.username}. Attempts Remaining: {lab_attempts}.")
                time.sleep(2)

        # Quitting Driver For Failure To Find Lab Upload URL.
        logging.info(msg=f"Could Not Find Lab Upload URL For {self.username}. Attempts Expired. Quitting Driver.")
        self.driver.quit()

    def labs_and_weeks(self,lab_upload_url: str):
        """
        The function finds all the available labs, and weeks to upload to.
        This function can only be called if login_to_samvidha() returns True.

        It is utilizing the new WebDriverWait.

        :param lab_upload_url: The URL obtained by calling find_lab_upload_url().

        :return: A dictionary, with keys "labs" and "weeks" and values as lists of strings. If the dictionary is empty, the driver will quit.
        """
        self.driver.get(lab_upload_url)
        labs_and_weeks = dict()

        labs_available_attempts = 0
        while labs_available_attempts < 5:
            try:
                # Waiting For The Lab Select Element.
                lab_select_element = WebDriverWait(self.driver, timeout=2).until(
                    ExpecCond.presence_of_element_located((By.ID, "sub_code"))
                )

                # Creating Select Object For Labs.
                lab_select = Select(lab_select_element)
                labs = [opt.text for opt in lab_select.options]
                labs_and_weeks["labs"] = labs[1:]

                # Waiting For Weeks Element.
                weeks_element = WebDriverWait(self.driver, timeout=2).until(
                    ExpecCond.presence_of_element_located((By.ID, "week_no"))
                )

                # Creating Select Object For Weeks.
                week_select = Select(weeks_element)
                weeks = [opt.text for opt in week_select.options]
                labs_and_weeks["weeks"] = weeks

                logging.info(f"Labs And Weeks Succcessfully Found For {self.username}.")
                return labs_and_weeks

            except selenium.common.TimeoutException:
                labs_available_attempts += 1
                logging.info(
                    f"Could Not Find Labs And Weeks For {self.username}. Attempts Remaining: {labs_available_attempts}")

            except Exception as LabAndWeekException:
                labs_available_attempts += 1
                logging.info(
                    f"Could Not Find Labs And Weeks For {self.username}. Due To {LabAndWeekException}. Attempts Remaining: {labs_available_attempts}"
                )

        logging.info(f"Could Not Find Labs And Weeks For {self.username}. Quitting Session.")
        self.driver.quit()
        return labs_and_weeks

    def week_date(self, lab_index: int, week_index) -> str:
        """
        The function finds the deadline for the given lab_index and week_index according to the
        previous labs_and_weeks() functions.
        :param lab_index: The index for the lab according to the
        :param week_index:
        :return: str, the deadline for the given lab and week. Empty string in case of errors.

        It is utilizing the new WebDriverWait.
        """
        
        self.driver.get("https://samvidha.iare.ac.in/home?action=labrecord_std")
        date_attempts = 0
        date = ""
        while date_attempts < 5:
            try:
                # Waiting For Lab Select Element.
                lab_select_element = WebDriverWait(self.driver, timeout=2).until(
                    ExpecCond.presence_of_element_located((By.ID, "sub_code"))
                )

                # Creating Select Object For Labs.
                lab_select = Select(lab_select_element)

                # Passing lab_index To Select Lab.
                lab_select.select_by_index(lab_index)

                # Waiting For Week Select Element.
                weeks_element = WebDriverWait(self.driver, timeout=2).until(
                    ExpecCond.presence_of_element_located((By.ID, "week_no"))
                )

                # Creating Select Object For Weeks.
                week_select = Select(weeks_element)

                # Passing week_index To Select Week.
                week_select.select_by_index(week_index)

                # Waiting For The Lab Deadline Element.
                lab_deadline_element = WebDriverWait(self.driver, timeout=2).until(
                    ExpecCond.presence_of_element_located((By.ID, "lab_exp_date"))
                )

                date += lab_deadline_element.text
                logging.info(f"Date Successfully Found For {self.username}.")
                return date

            except selenium.common.TimeoutException:
                date_attempts += 1
                logging.info(
                    f"Could Not Find Date For {self.username}. Attempts Remaining: {date_attempts}."
                )

            except Exception as DateError:
                date_attempts += 1
                logging.info(
                    f"Could Not Find Date For {self.username}, Due To {DateError}. Attempts Remaining: {date_attempts}."
                )

        logging.info(f"Could Not Find Date For {self.username}. Quitting Driver.")
        return date

    def upload_pdf(self, url: str, title: str, filepath: str, week_index: int, lab_index: int) -> tuple:
        """
        This is the final function that uploads the pdf, to the given week_index week, in lab_index lab as title.

        :param title: The title that the user wants to pass for their upload.
        :param filepath: This is the user's file in pdfs/
        :param week_index: This is the index with respect to "labs" from labs_and_weeks().
        :param lab_index: This is the index with respect to "weeks" from labs_and_weeks().

        :return: A tuple containing 3 things, a status code, a status message, and samvidha related details in that order.

        This function will not be containing WebDriverWait, As It Is Misbehaving.
        """
        self.driver.get(url)
        lab_upload_attempts = 0
        while lab_upload_attempts < 5:
            try:
                # Finding Select Elements.
                lab_element = self.driver.find_element(by=By.ID, value="sub_code")
                week_element = self.driver.find_element(by=By.ID, value="week_no")

                # Creating Select Objects
                lab_select = Select(lab_element)
                week_select = Select(week_element)

                # Passing Keys To The Elements.
                lab_select.select_by_index(lab_index)
                time.sleep(1)
                week_select.select_by_index(week_index)
                time.sleep(1)

                # Passing Title.
                title_element = self.driver.find_element(by=By.ID, value="exp_title")
                title_element.send_keys(title)
                time.sleep(1)

                # Passing Lab File.
                lab_file_element = self.driver.find_element(By.ID, value="prog_doc")
                lab_file_element.send_keys(filepath)
                time.sleep(1)

                # Clicking Submit Button.
                submit_button = self.driver.find_element(by=By.ID, value="LAB_OK")
                submit_button.click()
                time.sleep(2.5)

                # Finding Status Elements.
                status_element = self.driver.find_element(by=By.ID, value="swal2-title")

                if "success" in status_element.text.lower():
                    logging.info(f"The Lab File Was Uploaded Successfully For {self.username}.")
                    return 200, "Successful Upload", ""
                elif "date not found" in status_element.text.lower():
                    logging.info(f"The Upload For {self.username} Was Assigned No Date.")
                    return 400, "Date Not Assigned", f"{status_element.text}"
                elif "pdf" in status_element.text.lower():
                    logging.info(f"The Uploaded File Was Not A PDF For {self.username}.")
                    return 401, "Not A PDF File", f"{status_element.text}"
                elif "duplicate" in status_element.text.lower():
                    logging.info(f"Duplicate Record Was Uploaded By {self.username}.")
                    return 402, "Duplicate Lab Record", f"{status_element.text}"
                else:
                    logging.info(f"The Lab Upload Has Exceeded Deadline For {self.username}.")
                    return 403, "Uploaded Date Exceeded", f"{status_element.text}"

            except selenium.common.NoSuchElementException or selenium.common.ElementNotSelectableException:
                lab_upload_attempts += 1
                logging.info(
                    msg=f"Internal Samvidha Loading Error For {self.username}, {lab_upload_attempts} Time. Trying Again.")

            except selenium.common.exceptions.ElementClickInterceptedException:
                logging.info(f"The File Is Above 1MB For {self.username}. Quitting Driver.")
                self.driver.quit()
                return 404, "File Size Greater Than 1MB", ""
            except selenium.common.InvalidArgumentException:
                logging.info(msg=f"The Lab Path Or Name Is Not Correct For {self.username}")
                self.driver.quit()
                return 405, "Filepath Was Not Set Correctly", ""
            except Exception as LabUploadError:
                logging.info(msg=f"The Upload Failed For {self.username}, Due To {LabUploadError}. Quitting Driver.")
                self.driver.quit()
                return 201, "Unsuccessful Upload", f"{LabUploadError}"
                
        logging.info(
            msg=f"Failed To Upload PDF For {self.username}, As Attempts Expired."
        )
        self.driver.quit()
        return 201, "Unsuccessful Upload", ""
    
    def logout_from_samvidha(self):
        """
        This is the function that must be called at the end of any operation. The function logs
        out from samvidha.
        :return: True, for successful log-out, else, False.
        """

        logout_attempts = 0
        while logout_attempts < 5:
            try:
                # Simply Getting Log-Out URL.
                self.driver.get("https://samvidha.iare.ac.in/logout")
                logging.info(f"Log-Out Successful For {self.username}.")
                return True
            except Exception as Error:
                logout_attempts += 1
                logging.info(f"Log-Out Unsuccessful For {self.username}. Attempts Remaining: {logout_attempts}")

        logging.info(f"Log-Out Failed For {self.username}. Quitting Driver.")
        self.driver.quit()
        return False
    

# Features Related To ViewUploads.
    def lists_labs(self) -> list[str]:
        """
        The function lists all the labs available to show uploads for. This lab selects from
        the element bearing the ID "ddlsub_code" rather than the table from below.
        :return: A list containing all the labs, empty in-case of error to acquire them.

        It is using the new WebDriverWait
        """
        # Getting Lab Upload URL
        labs_attempts = 0
        while labs_attempts < 5:
            try:
                # Waiting For The Lab Select Element.
                lab_select_element = WebDriverWait(self.driver, timeout=2).until(
                    ExpecCond.presence_of_element_located((By.ID, "ddlsub_code"))
                )

                # Extracting All The Options.
                lab_select = Select(lab_select_element)
                labs = [opt.text for opt in lab_select.options]
                if labs:
                    logging.info(msg=f"Labs Found For {self.username}.")
                    return labs[1:]

            except selenium.common.TimeoutException:
                labs_attempts += 1
                logging.info(msg=f"Labs Not Found For {self.username}. Attempts Remaining: {5 - labs_attempts}")

            except Exception as LabsError:
                labs_attempts += 1
                logging.info(
                    msg=f"""
                    Labs Not Found For {self.username}, Due To {LabsError}. Attempts Remaining: {5 - labs_attempts}.
                    """
                )

        logging.info(msg=f"Failed To Acquire Labs For {self.username}. Quitting Driver.")
        self.driver.quit()
        return []

    def select_and_click(self, lab: int) -> bool:
        """
        The function selects the lab according to the index sent,
        clicks on the submit button.
        :param lab: Lab index for selecting. Must be select based on 1-Indexing.
        :return: True, if select was successful. Else, False.

        It is using the new WebDriverWait.
        """
        click_attempts = 0
        while click_attempts < 5:
            try:
                # Waiting For The Lab Select Element.
                lab_select_element = WebDriverWait(self.driver, timeout=2).until(
                    ExpecCond.presence_of_element_located((By.ID, "ddlsub_code"))
                )

                # Selecting A Lab Using Select Object.
                lab_select = Select(lab_select_element)
                lab_select.select_by_index(lab)

                # Waiting For Show Submitted Button.
                show_submitted_button = WebDriverWait(self.driver, timeout=2).until(
                    ExpecCond.presence_of_element_located((By.ID, "search"))
                )

                # Clicking On The Show Submitted Button.
                show_submitted_button.click()
                time.sleep(2.5)

                logging.info(msg=f"Successfully Executed Select And Click For {self.username}.")
                return True

            except selenium.common.TimeoutException:
                logging.info(
                    msg=f"Could Not Select And Click For {self.username}. Attempts Remaining: {5 - click_attempts}."
                )
                click_attempts += 1

            except Exception as SelectAndClickError:
                logging.info(
                    msg=f"""
                    Could Not Select And Click For {self.username}, Due To {SelectAndClickError}
                     Attempts Remaining: {5 - click_attempts}."""
                )
                click_attempts += 1

        logging.info(f"Finally, Could Not Select And Click For {self.username}. Quitting Driver.")
        self.driver.quit()
        return False

    def displaying_lab_data(self) -> dict:
        """
        The function displays all the details of uploaded lab sheets, like Academic
        Year, Subject Code, Experiment Title, Week Number, Marks, And Link To The
        PDF Uploaded. This function must be called only after select_and_click() returns True.

        :return: dict of dicts, containing all these values under an index as key, and these
        details as values, empty dict in case of errors.
        """
        upload_data = dict()
        display_data_attempts = 0
        while display_data_attempts < 5:
            try:
                # Getting The Page Source.
                page_source = self.driver.page_source

                # Creating Soup Object And Passing The Source.
                soup = BeautifulSoup(page_source, "html.parser")
                view_upload_table = soup.find(id="example2")

                # Finding The Table-Body, And Hence The Rows.
                table_body_element = view_upload_table.find(id="result")
                rows = table_body_element.find_all("tr")

                # Filling Up The Dictionary.
                index = 0
                for row in rows:
                    # Finding All The Rows In The Table.
                    table_data = row.find_all("td")[1:]

                    # Creating Data Dictionary.
                    data = dict()

                    # Adding All The Details, Except Link
                    data["Academic Year"] = table_data[0].text
                    data["Course Code"] = table_data[1].text
                    data["Title"] = table_data[2].text
                    data["Week Number"] = table_data[3].text
                    data["Marks"] = table_data[4].text

                    # Finding PDF Link.
                    anchor = table_data[6].find("a")
                    link = anchor["href"]
                    data["Link To PDF"] = link

                    # Adding Data To Upload Data.
                    upload_data[index] = data

                    # Incrementing Index.
                    index += 1

                logging.info(msg=f"Successfully Found Upload Details For {self.username}.")
                return upload_data

            except selenium.common.TimeoutException:
                display_data_attempts += 1
                logging.info(
                    msg=f"""
                    Failed To Find Upload Data For {self.username}. Attempts Remaining: {5 - display_data_attempts}.
                        """
                )

            except Exception as UploadDataError:
                display_data_attempts += 1
                logging.info(
                    msg=f"""
                    Failed To Find Upload Data For {self.username}, Due To {UploadDataError}
                    Attempts Remaining: {5 - display_data_attempts}.
                """)

        logging.info(msg=f"Failed For Find Lab Upload Data For {self.username}. Quitting Driver")
        self.driver.quit()
        return upload_data
    
    def find_title(self, week: int) -> str:
        """
        The function finds the title for a particular week, for particular lab.
        The week must be passed, but the lab must be passed to select_and_click().
        :return: The title for the week, for the lab, If found, else empty string.
        """
        view_upload_attempts = 0
        while view_upload_attempts < 5:
            try:
                # Finding The Upload Table.
                source = self.driver.page_source

                # Creating Soup Object.
                soup = BeautifulSoup(source, features="html.parser")

                # Finding All Tables.
                table = soup.find_all("table")[0]

                # Finding All The Rows.
                rows = table.find("tbody").find_all("tr")

                for row in rows[1:]:
                    extracted_week = row.find("td")
                    if int(extracted_week.text.removeprefix("Week-")) == week:
                        extracted_title = row.find_all("td")[2]
                        logging.info(f"Title Found For {self.username}.")
                        return extracted_title.text

                logging.info(
                    f"The Title Has Not Been Found For {self.username}. Attempts Remaining: {view_upload_attempts - 5}"
                )
                view_upload_attempts += 1

            except Exception as TitleError:
                logging.info(
                    msg=f"Title Has Not Been Found For Given Week Number For {self.username}, Due To {TitleError}"
                )
                view_upload_attempts += 1

        logging.info(
            msg=f"Could Not Find Title For {self.username}. Quitting Driver."
        )
        self.driver.quit()
        return str()
    
async def user_session(username,password):
    """
    This Function starts a user session.
    
    :param username: username of the user
    :param password: password of the user
    
    :return: returns my_lab_upload session and the url of the lab upload"""
    my_lab_upload = HeadlessLabUpload(username, password)
    my_lab_upload.login_to_samvidha()
    url = "https://samvidha.iare.ac.in/home?action=labrecord_std"
    return my_lab_upload,url

async def get_lab_details(bot,chat_id):
    """
    This function retreives the lab details from samvidha and stores it in labuploads database.
    
    :param bot: Client of pyrogram
    :param chat_id: chat_id of the user based on the message received."""
    get_credentials = await pgdatabase.retrieve_credentials_from_database(chat_id)
    username, password = get_credentials
    my_lab_upload,url = await user_session(username,password)
    # Fetching the labs and weeks data
    labs_and_weeks_data = my_lab_upload.labs_and_weeks(url)
    labs_data = labs_and_weeks_data["labs"]
    weeks_data = labs_and_weeks_data["weeks"]
    try:
        # Storing the labs and weeks data in the database
        await tdatabase.store_lab_info(chat_id,subject_index=None,week_index=None,subjects=labs_data,weeks=weeks_data)
    except Exception as e:
        logging.info(msg=f"there is an error storing lab info to the database. the error is {e}")

async def upload_lab_pdf(bot,message):
    """
    This Function is used to upload the the pdf to the samvidha by retreiving the required data from the database.

    :param bot: Pyrogram Client.
    :param message: message sent by the user.
    
    :return: None
    """
    # chat_id of the user based on the message sent by the user
    chat_id = message.chat.id
    message_sent_when_started = await bot.send_message(chat_id,"Initiated retrieval of necessary data for uploading.")
    # Retreives username and password from the postgres database.
    get_credentials = await pgdatabase.retrieve_credentials_from_database(chat_id)
    username, password = get_credentials
    # starting user session and getting session and url
    my_lab_upload,url = await user_session(username,password)
    # Retreiving the Entered title, subject_index, week_index
    title,subject_index,week_index = await tdatabase.fetch_indexes_and_title_lab_info(chat_id)
    # Get all subjects from the database
    subjects_data = await tdatabase.fetch_lab_subjects_from_lab_info(chat_id)
    # Deserializing the data retreived
    selected_subject_name = json.loads(subjects_data[0])
    # Fetching Last date to upload the selected Subject and week
    last_date_to_upload = my_lab_upload.week_date(subject_index,week_index)
    # Folder name containg pdfs
    pdf_folder = "pdfs"
    # Check Whether the pdf is present or not, If the pdf is present gets the compression status
    check_present , check_compress = await labs_handler.check_recieved_pdf_file(bot,chat_id)
    if check_present:
        # According to the compression status the pdf file is selected to uplaod
        if check_compress is True:
            pdf_folder = os.path.join(pdf_folder,f"C-{chat_id}-comp.pdf")
        else:
            pdf_folder = os.path.join(pdf_folder,f"C-{chat_id}.pdf")
    message_text_before_uploading = f"""
```UPLOAD INITIATED
⫸ STATUS : UPLOADING

⫸ LAST DATE TO SUBMIT : {last_date_to_upload}

⫸ UPLOAD DETAILS :

Title : {title} 

SUBJECT : {selected_subject_name[subject_index-1]}

WEEK : {f"Week - {week_index+1}"}

```
"""
    message_before_start_upload = await bot.edit_message_text(chat_id,message_sent_when_started.id,message_text_before_uploading)
    # Started uploading the pdf to Samvidha based on all the data given to the function
    upload_pdf_to_samvidha = my_lab_upload.upload_pdf(
        url=url, # Url of the lab record
        filepath=os.path.abspath(pdf_folder), # filepath of the pdf
        title=title, # title of the subject
        lab_index=subject_index, # Selected subject index
        week_index=week_index # Selected week index
    )
    STATUS_CODE ,STATUS_MESSAGE, STATUS_SAMVIDHA = upload_pdf_to_samvidha
    ERROR_STATUS_CODES = [400,401,402,403,404,405,201] # Error codes
    if STATUS_CODE in ERROR_STATUS_CODES:# Checks if received status code is error or not.
        UNSUCCESSFULL_UPLOAD_MESSAGE = f"""
    ```UPLOAD FAILED
⫸ STATUS : {STATUS_CODE} ERROR

⫸ ERROR : {STATUS_MESSAGE}

⫸ ERROR REASON : {STATUS_SAMVIDHA}

⫸ LAST DATE TO SUBMIT : {last_date_to_upload}

⫸ UPLOAD DETAILS :

● Title : {title} 

● SUBJECT : {selected_subject_name[subject_index-1]}

● WEEK : {f"Week - {week_index+1}"}

    ```
    """
        await labs_handler.remove_pdf_file(bot,chat_id) # Removes the Pdf from the pdf folder
        await tdatabase.delete_indexes_and_title_info(chat_id) # Delete the selected index values
        await bot.edit_message_text(chat_id,message_before_start_upload.id,UNSUCCESSFULL_UPLOAD_MESSAGE)
    else:
        SUCCESSFULL_UPLOAD_MESSAGE = F"""
    ```UPLOAD SUCCESS
⫸ STATUS : {STATUS_MESSAGE}

⫸ LAST DATE TO SUBMIT : {last_date_to_upload}

⫸ Upload details :

● Title : {title}

● SUBJECT : {selected_subject_name[subject_index-1]}

● WEEK : {f"Week - {week_index+1}"}

    ``` 
    """
        await labs_handler.remove_pdf_file(bot,chat_id)# Removes the Pdf from the pdf folder
        await tdatabase.delete_indexes_and_title_info(chat_id)# Delete the selected index values
        await bot.edit_message_text(chat_id,message_before_start_upload.id,SUCCESSFULL_UPLOAD_MESSAGE)
    await buttons.start_user_buttons(bot,message) # Starts the user buttons.
