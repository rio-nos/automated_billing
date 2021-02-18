from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from time import sleep
from math import ceil


class CityOfSalem:
    def __init__(self, path, options, username, password):
        self.username = username
        self.password = password
        self.individuals = 6
        self.balance = None
        self.pay = None
        self.login_timeout = 10
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
            self.driver.get('https://egov.cityofsalem.net/eebpp/Account/Login')
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="UserName"]'))).send_keys(self.username)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Password"]'))).send_keys(self.password)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[class="btn-u pull-right"][type="submit"]'))).submit()
        except TimeoutException:
            print("TimeoutException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()

    def get_balance(self):
        try:
            balance = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'p[class="form-control-static"]')))
            text_balance = balance[3].text.split()[0]
            if any(x in text_balance for x in ['(', ')']):
                self.balance = -float(text_balance[2:-1])
            else:
                self.balance = float(text_balance[1:])
            print(self.balance)
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
            print("Extra credit on balance amount. We have paid more than is required on the bill!")
        else:
            print("Your balance is: {}".format(self.balance))
            sleep(1)
            self.pay = ceil((self.balance / self.individuals) * 100) / 100.0
            print("Each person will pay: {}".format(self.pay))
            sleep(1)
            while(True):
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

    def make_payment(self):
        try:
            # Drop-down menu contains options that look like the following:
            # We want to start with index 1 up to self.individuals
            # to split the cost for all saved payment methods in City of Salem account.
            for i in range(1, self.individuals):
                # Navigate to page that'll redirect us to payment page => Pay Now button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'a[class="btn btn-success btn-xs"'))).click()
                # Onto the payment page => Continue button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button[class="btn-u"][type="submit"]'))).submit()
                # Change payment amount.
                pay_box = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="paymentAmount"]')))
                pay_box.click()
                pay_box.clear()
                amount = ''
                if i == 3:
                    amount = str(self.pay*2)
                    pay_box.send_keys(amount)
                else:
                    amount = str(self.pay)
                    pay_box.send_keys(amount)
                select = Select(self.driver.find_element_by_xpath('//*[@id="savedPaymentMethodRef"]'))
                select.select_by_index(i)
                # Continue onto confirmation page.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="continue"]'))).click()
                print("Payment amount of {}.".format(amount))
                while True:
                    confirm = input("Confirm? [Y/N]: ").strip()
                    if confirm in ["Y", "y"]:
                        print("Confirming payment...")
                        break
                    elif confirm in ["N", "n"]:
                        print("Continuing next payment.")
                        self.driver.get('https://egov.cityofsalem.net/eebpp/MyAccounts/AccountSummary/36877')
                        continue
                    else:
                        print("Please try a valid response.")
                # Confirm payment.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="confirm"]'))).click()
                sleep(2)
                # Navigate to dashboard.
                self.driver.get('https://egov.cityofsalem.net/eebpp/MyAccounts/AccountSummary/36877')
            print("Quitting for loop. About to abort.")
            sleep(7)
        except NoSuchElementException:
            print("NoSuchElementException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()
        except TimeoutException:
            print("TimeoutException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()
