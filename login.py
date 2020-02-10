from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


def login():
    driver = webdriver.Chrome()
    driver.get("https://nuscast.ap.panopto.com/Panopto/")
    input(
        "Select the desired login method and click 'Sign in', "
        "then press Enter in this console"
    )

    with open("secrets.txt") as f:
        username_input = driver.find_element_by_id("userNameInput")
        password_input = driver.find_element_by_id("passwordInput")
        sign_in = driver.find_element_by_id("submitButton")

        class Secrets:
            def __init__(self):
                self.username = None
                self.password = None

            def set_username(self, username):
                self.username = username

            def set_password(self, password):
                self.password = password

        username, password = f.readlines()
        secrets = Secrets()
        secrets.set_username(username.strip())
        secrets.set_password(password.strip())

    username_input.send_keys(secrets.username)
    password_input.send_keys(secrets.password)
    sign_in.click()

    return driver
