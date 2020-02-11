from seleniumwire import webdriver
from selenium.webdriver.support.wait import WebDriverWait

# from selenium.webdriver.chrome.options import Options


def login():
    # options = Options()
    # options.add_argument("--autoplay-policy=no-user-gesture-required")

    options = {"autoplay-policy": "no-user-gesture-required"}
    driver = webdriver.Chrome(seleniumwire_options=options)
    driver.get("https://nuscast.ap.panopto.com/Panopto/")

    input(
        "Select the desired login method and click 'Sign in', "
        "then press Enter in this console"
    )

    class Secrets:
        def __init__(self):
            self.username = None
            self.password = None

        def set_username(self, username):
            self.username = username

        def set_password(self, password):
            self.password = password

    try:
        with open("secrets.txt") as f:
            username_input = driver.find_element_by_id("userNameInput")
            password_input = driver.find_element_by_id("passwordInput")
            sign_in = driver.find_element_by_id("submitButton")

            username, password = f.readlines()
            secrets = Secrets()
            secrets.set_username(username.strip())
            secrets.set_password(password.strip())

        username_input.send_keys(secrets.username)
        password_input.send_keys(secrets.password)
        sign_in.click()
    except FileNotFoundError:
        print("Credentials file 'secrets.txt' not found.")
        input(
            "Please key in your credentials manually and sign in,"
            "then press Enter in the console"
        )

    return driver
