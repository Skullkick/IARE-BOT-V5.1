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

