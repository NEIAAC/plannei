from asyncio import subprocess
import random
from PySide6.QtCore import QThread, Signal

from csv import DictReader, __version__ as csv_version
from openpyxl import load_workbook, __version__ as openpyxl_version
from selenium import webdriver
from selenium.webdriver.common.by import By
from enum import Enum

from utils.logger import logger

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
]

class BrowserChoice(Enum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"

BASE_URL = "https://inforestudante.uc.pt"
LOGIN_URL = f"{BASE_URL}/nonio/security/login.do"
ENROLL_URL = f"{BASE_URL}/nonio/inscturmas/init.do"


class BrowserThread(QThread):
    outputSignal = Signal(str, str)

    def __init__(
        self,
        loginEmail: str,
        loginPassword: str,
        browserChoice: BrowserChoice,
        headless: bool,
        enrollmentIndex: int,
        tablePath: str = "",
    ):
        super().__init__()
        self.loginEmail = loginEmail
        self.loginPassword = loginPassword
        self.browserChoice = browserChoice
        self.headless = headless
        self.enrollmentIndex = enrollmentIndex
        self.tablePath = tablePath


    def output(self, text: str, level="INFO"):
        logger.log(level, text)
        self.outputSignal.emit(text, level)

    def readTable(self) -> tuple[list[dict[str, str]], list[str]]:
        if self.tablePath.endswith(".csv"):
            logger.info(
                f"Using native CSV {csv_version} module to read {self.tablePath}"
            )
            records = []
            with open(self.tablePath, mode="r", encoding="utf-8") as csvfile:
                reader = DictReader(csvfile)
                headers = reader.fieldnames
                if not headers:
                    raise ValueError("CSV file has no headers")
                logger.info(f"Headers found in CSV: {len(headers)}")
                for row in reader:
                    records.append(
                        {
                            key: (value if value else "")
                            for key, value in row.items()
                        }
                    )
        elif self.tablePath.endswith(".xlsx"):
            logger.info(
                f"Using openpyxl {openpyxl_version} to read {self.tablePath}"
            )
            workbook = load_workbook(filename=self.tablePath, data_only=True)
            logger.info(
                f"Loaded workbook with {len(workbook.sheetnames)} sheets"
            )
            sheet = workbook.active
            if not sheet:
                raise ValueError("Excel file has no sheets")
            logger.info(
                f"Active sheet: {sheet.title}, {sheet.max_row} rows, {sheet.max_column} columns"
            )
            headers = [str(cell.value) for cell in sheet[1] if cell.value]
            logger.info(f"Headers found: {len(headers)}")
            if not headers:
                raise ValueError("Excel file has no headers")
            records = []
            for row in sheet.iter_rows(min_row=2, values_only=True):  # type: ignore
                logger.debug(f"Row data: {row}")
                record = {
                    headers[i]: (value if value else "")
                    for i, value in enumerate(row)
                    if i < len(headers)
                }
                records.append(record)
        else:
            raise ValueError("Unsupported file extension")

        return records, list(headers)

    def setupChromium(self) -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-default-apps")
        options.add_argument("--mute-audio")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--remote-allow-origins=*")
        options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
        if self.headless:
            options.add_argument("--headless")
        options.page_load_strategy = "eager"
        service = webdriver.ChromeService(log_output=subprocess.DEVNULL)
        return webdriver.Chrome(options=options, service=service)

    def setupFirefox(self) -> webdriver.Firefox:
        options = webdriver.FirefoxOptions()
        options.set_preference("permissions.default.desktop-notification", 2)
        options.set_preference("permissions.default.image", 2)
        options.set_preference("dom.push.enabled", False)
        options.set_preference("dom.webnotifications.serviceworker.enabled", False)
        options.set_preference("dom.webnotifications.enabled", False)
        options.set_preference("general.useragent.override", random.choice(USER_AGENTS))
        if self.headless:
            options.add_argument("--headless")
        options.page_load_strategy = "eager"
        service = webdriver.FirefoxService(log_output=subprocess.DEVNULL)
        return webdriver.Firefox(options=options, service=service)

    def run(self):
        inputs = self.__dict__.copy()
        inputs.pop("loginEmail", False)
        inputs.pop("loginPassword", False)

        logger.info(f"Starting browser thread with input parameters: {inputs}")

        self.output("...")

        with logger.catch():
            try:
                if self.browserChoice == BrowserChoice.CHROMIUM:
                    driver = self.setupChromium()
                elif self.browserChoice == BrowserChoice.FIREFOX:
                    driver = self.setupFirefox()
                else:
                    raise Exception("Invalid browser choice")
            except Exception as error:
                self.output(
                    f"No supported browser found, you need to have the selected browser installed on your system: {error}",
                    "ERROR",
                )
                return

            self.output(f"{driver.name.capitalize()} browser initialized")
            self.output(f"Navigating to {LOGIN_URL}")
            driver.get(LOGIN_URL)

            if driver.current_url != LOGIN_URL:
                self.output("Already logged in")
            else:
                username_input = driver.find_element(By.CSS_SELECTOR, "input#username")
                password_input = driver.find_element(By.CSS_SELECTOR, "input#password1")
                username_input.send_keys(self.loginEmail)
                password_input.send_keys(self.loginPassword)
                self.output("Filled login form")
                login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                login_button.click()
                self.output("Clicked login button")
                if driver.current_url == LOGIN_URL:
                    self.output("Login failed, check your credentials", "ERROR")
                    return
                self.output("Login successful")

            self.output(f"Now at {driver.current_url}")
            self.output(f"Navigating to {ENROLL_URL}")
            driver.get(ENROLL_URL)
            self.output(f"Now at {driver.current_url}")

            tableBody = driver.find_element(By.CSS_SELECTOR, "table.displaytable > tbody")
            chosenEnrollment = tableBody.find_element(By.CSS_SELECTOR, f"tr:nth-of-type({self.enrollmentIndex})")

            chosenEnrollmentText = chosenEnrollment.find_element(By.CSS_SELECTOR, "td:first-child").text
            chosenEnrollmentLink = chosenEnrollment.find_element(By.CSS_SELECTOR, "td:last-child > div > a").get_attribute("href")

            if not chosenEnrollmentLink:
                self.output("No enrollment link found", "ERROR")
                return

            self.output(f"Proceeding to enrollment in {chosenEnrollmentText}")
            driver.get(chosenEnrollmentLink)

            self.output(f"Now at {driver.current_url}")
