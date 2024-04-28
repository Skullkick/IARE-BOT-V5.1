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
