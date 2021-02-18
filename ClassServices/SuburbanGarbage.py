from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from time import sleep
from math import ceil


class SuburbanGarbage:
    def __init__(self, path, options, username, password):
        self.username = username
        self.password = password
        self.individuals = 6
        self.balance = None
        self.pay = None
        self.login_timeout = 15
        self.dashboard_timeout = 20
        self.driver = None
        self.path = path
        self.options = options

    def init_driver(self):
        self.driver = webdriver.Chrome(self.path, options=self.options)

    def display_info(self):
        print("    Username: " + self.username)
        print("    Individuals: " + str(self.individuals))
        print("    Balance: " + str(self.balance))
        print("    Pay: " + str(self.pay) + "\n")

    # Ask the user for custom values. Otherwise, use default values in __init__().
    def prompt_user(self):
        print("\n\nService: " + self.__class__.__name__ + "\n")
        self.display_info()
        while True:
            confirm = input("\nEnter account information manually? (Y/N): ").strip()
            if confirm in ["Y", "y"]:
                while True:
                    try:
                        self.individuals = int(input("\nEnter # of individuals (integer): ").strip())
                        self.balance = float(input("\nEnter balance amount (decimal): ").strip())
                        self.pay = float(input("\nEnter pay amount (decimal): ").strip())
                        if self.pay > self.balance:
                            print("Cannot have the pay be greater than the balance.\nTry again!")
                            continue
                        break
                    except ValueError:
                        print("Error: unable to convert input.\nTry again!")
                        continue
                break
            elif confirm in ["N", "n"]:
                print("Using default values.")
                break
            else:
                print("\nTry again.")
                continue

    def login(self):
        try:
            self.driver.get('https://secure.myonlinebill.com/mob/user/login.do?clientId=MTA4OTY=')
            sleep(1)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="userId"]'))).send_keys(self.username)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="password"]'))).send_keys(self.password)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="signInBtn"]'))).click()
        except NoSuchElementException:
            print("NoSuchElementException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()
        except TimeoutException:
            print("TimeoutException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()

    def get_balance(self):
        try:
            try:
                WebDriverWait(self.driver, 1).until(EC.alert_is_present(), 'Waiting for pop up')
                alert = self.driver.switch_to.alert
                alert.accept()
                print("Alert accepted")
            except TimeoutException:
                print("Nested TimeoutException occurred. Executing finally block.")
            finally:
                balance = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="billTable"]/tbody/tr/td[4]/ul/li')))
                self.balance = float(balance.text.strip()[1:])
        except NoSuchElementException:
            print("NoSuchElementException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()
        except TimeoutException:
            print("TimeoutException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()

    def validate(self):
        if self.balance == 0.0:
            print("No balance to pay")
        elif self.balance < 0.0:
            print("Extra credit on balance amount. We have paid more than is required on the bill! Excellent :)")
        else:
            print("\nNumber of individuals paying: {}".format(self.individuals))
            print("\nYour balance is: {}".format(self.balance))
            self.pay = ceil((self.balance / self.individuals) * 100) / 100.0
            print("Each person will pay: {}".format(self.pay))
            while True:
                confirm = input("Confirm? [Y/N]: ").strip()
                if confirm in ["Y", "y"]:
                    self.make_payment()
                    break
                elif confirm in ["N", "n"]:
                    print("No payment was made.")
                    break
                else:
                    print("No valid response. Try again.")
                    continue
        return 1

    def make_payment(self):
        try:
            # We want to start with index 1 up to self.individuals
            flag = False
            for i in range(1, self.individuals):
                # Navigate to payment page.
                payment_box = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="amount"]')))
                if not flag:
                    WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="payNowLink"]'))).click()
                    # Retrieve payment box. Clear and add quantity.
                payment_box.clear()
                if i == 5:
                    amount = str(self.pay*2)
                    payment_box.send_keys(amount)
                else:
                    amount = str(self.pay)
                    payment_box.send_keys(amount)
                # Select which payment option to use => Pay Now
                payment_option = Select(WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="paymentTime"]'))))
                payment_option.select_by_index(1)
                # Choose which payment method to use.
                payment_type = Select(WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="paymentOption"]'))))
                payment_type.select_by_index(i)
                sleep(1)
                # Click 'Yes, I agree' button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'label[for="agreeY"]'))).click()
                print("Payment amount of {}.".format(amount))
                while True:
                    confirm = input("Confirm? [Y/N]: ").strip()
                    if confirm in ["Y", "y"]:
                        print("Confirming payment...")
                        flag = False
                        break
                    elif confirm in ["N", "n"]:
                        print("Continuing next payment.")
                        flag = True
                        break
                    else:
                        print("Please try a valid response.")
                if flag:
                    continue
                # Click 'Next' button to continue.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="paymentBtn"]'))).click()
                # Click "Next" button to confirm payment.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="paymentProcessBtn"]'))).click()
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="doneBtn"]'))).click()
                print("Success!")
        except Exception as e:
            print("Error occurred.\nQuiting driver...")
            print("Error:\n{}".format(e))
            self.driver.close()
            self.driver.quit()