from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from time import sleep
from math import ceil


class Xfinity:
    def __init__(self, path, options, username, password):
        self.driver = None
        self.path = path
        self.options = options
        self.username = username
        self.password = password
        self.dashboard_timeout = 1000
        self.login_timeout = 60
        self.individuals = 3
        self.balance = 111.0
        self.pay = 37.0

    def init_driver(self):
        self.driver = webdriver.Chrome(self.path, options=self.options)

    def display_info(self):
        print("\n\nService: " + self.__class__.__name__ + "\n")
        print("    Username: " + self.username)
        print("    Individuals: " + str(self.individuals))
        print("    Balance: " + str(self.balance))
        print("    Pay: " + str(self.pay) + "\n")

    # Ask the user for custom values. Otherwise, use default values in __init__().
    def prompt_user(self):
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
                        return 1
                    except ValueError:
                        print("Error: unable to convert input.\nTry again!")
                        continue
                break
            elif confirm in ["N", "n"]:
                print("Using default values.")
                return 0
            else:
                print("\nTry again.")
                continue

    def login(self):
        try:
            self.driver.get('https://customer.xfinity.com/#/billing')
            sleep(1)
            while True:
                confirm = input("\nEntered log-in information? (Y/N): ").strip()
                if confirm in ["Y", "y"]:
                    return 1
                elif confirm in ["N", "n"]:
                    return 0
                else:
                    print("\nTry again.")
                    continue
        except TimeoutException:
            print("TimeoutException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()

    def get_balance(self):
        try:
            balance = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'span[class="price price--fancy mb0"][price="billOverviewBalanceDue"]')))
            self.balance = float(balance.text[1:])
            while True:
                confirm = input("Continue? [Y/N]: ")
                if confirm in ["Y", "y"]:
                    return 1
                elif confirm in ["N", "n"]:
                    return 0
                else:
                    print("Please try again.")
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
            print("Your balance is: {}".format(self.balance))
            sleep(1)
            self.pay = ceil((self.balance / self.individuals) * 100) / 100.0
            print("Each person will pay: {}".format(self.pay))
            sleep(1)
            while True:
                confirm = input("Confirm? [Y/N]: ").strip()
                if confirm in ["Y", "y"]:
                    return self.make_payment()
                elif confirm in ["N", "n"]:
                    print("No payment was made.")
                    break
                else:
                    print("No valid response. Try again.")
                    continue
        return 1

    def make_payment(self):
        try:
            # Navigate to payment page => 'Make a payment' button.
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[class="button button--primary"][ng-href="https://payments.xfinity.com/new"]'))).send_keys("\n")
            # Retrieve all cards going to be used.
            cards = [card.text for card in WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'span[class="payment-instrument__text"]')))]
            flag = False
            for item in cards:
                if not flag:
                    payment_box = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="customAmount"]')))
                    print("Using card: " + str(item))
                    payment_box.send_keys(Keys.CONTROL, 'a')
                    payment_box.send_keys(Keys.BACKSPACE)
                    payment_box.send_keys(str(self.pay))
                # Find and click on payment method given current item in card_elements
                curr_element = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), '" + str(item) + "')]")))
                # Select that payment method.
                curr_element.click()
                print("Payment amount of {}.".format(str(self.pay)))
                while True:
                    confirm = input("Confirm? [Y/N]: ").strip()
                    if confirm in ["Y", "y"]:
                        print("Confirming payment...")
                        flag = False
                        break
                    elif confirm in ["N", "n"]:
                        print("Continuing next payment.")
                        flag = True
                        continue
                    else:
                        print("Please try a valid response.")
                if flag:
                    continue
                # Navigate to confirmation page => 'Continue' button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button[class="button button--primary"][type="submit"]'))).submit()
                # Retrieve current url before submitting payment, so that we wait for confirmation page to finish and be
                # consistent with the for loop
                current_url = self.driver.current_url
                # Confirm payment => 'Submit Payment' button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button[class="button button--primary"][type="submit"]'))).submit()
                # Wait until confirmation page is done loading before starting another payment.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.url_changes(current_url))
                # Make a new payment => 'New Payment' button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'a[class="button button--primary"][href="/new"]'))).click()
        except Exception as e:
            print("An error occurred attempting to make a payment. Exiting webdriver...")
            print(e)
            self.driver.close()
            self.driver.quit()
            return 0
        return 1

    def close(self):
        print("Exiting Xfinity driver.")
        self.driver.close()
        self.driver.quit()