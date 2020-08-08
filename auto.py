from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, \
    ElementClickInterceptedException
from secrets import cuser, cpass, suser, spass, puser, ppass, psc, xuser, xpass, tuser, tpass
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from time import sleep
from math import ceil

drive_path = './chromedriver.exe'


class CityOfSalem:
    def __init__(self, username, password):
        self.login_timeout = 10
        self.dashboard_timeout = 20
        self.username = username
        self.password = password
        self.individuals = 5
        self.balance = None
        self.pay = None
        self.driver = webdriver.Chrome(drive_path)

    def login(self):
        try:
            self.driver.get('https://egov.cityofsalem.net/eebpp/Account/Login')
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="UserName"]'))).send_keys(self.username)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Password"]'))).send_keys(self.password)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/form/div[4]/div/button'))).submit()
        except TimeoutException:
            print("TimeoutException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()

    def get_balance(self):
        try:
            balance = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located((By.XPATH,'/html/body/div[4]/div/div[2]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/p')))
            self.balance = float(balance.text[1:])
            print(self.balance)
            sleep(1)
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
        return 1

    def make_payment(self):
        try:
            # Drop-down menu contains options that look like the following:
            # 0 = Select, 1 = Francisco, 2 = Moni, 3 = Nemo, 4 = Nene
            # We want to start with index 1 up to and including 4
            # to split the cost for all saved payment methods in City of Salem account.
            for i in range(1, 5):
                # Navigate to epayment page.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[4]/div/div[2]/div/div[2]/div[1]/div/div[2]/div/div[4]/div/p/a'))).click()
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[4]/div/div/form/div[3]/div[4]/div/div/button'))).submit()
                # Change payment amount.
                pay_box = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="paymentAmount"]')))
                pay_box.click()
                pay_box.clear()
                pay_box.send_keys(str(0.01))
                select = Select(self.driver.find_element_by_xpath('//*[@id="savedPaymentMethodRef"]'))
                select.select_by_index(i)
                # Continue onto confirmation page.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="continue"]'))).click()
                # Confirm payment.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="confirm"]'))).click()
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


class SuburbanGarbage:
    def __init__(self, username, password):
        self.login_timeout = 15
        self.dashboard_timeout = 20
        self.username = username
        self.password = password
        self.individuals = 5
        self.balance = None
        self.pay = None
        self.driver = webdriver.Chrome(drive_path)

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
        return 1

    def make_payment(self):
        try:
            # Edit to self.individuals, change select_by_index for paymentType.
            for i in range(0, self.individuals - 4):
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="payNowLink"]'))).click()
                paymentBox = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="amount"]')))
                paymentBox.clear()
                paymentBox.send_keys(str(0.01))

                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="endUserPaymentForm"]/div[3]/div/div/button'))).click()
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="endUserPaymentForm"]/div[3]/div/div/div/ul/li[2]/a'))).click()
                sleep(1)
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="endUserPaymentForm"]/div[7]/div/div/button'))).click()
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="endUserPaymentForm"]/div[7]/div/div/div/ul/li[3]/a'))).click()
                sleep(1)
                # Click 'Yes, I agree' button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div/div[2]/div/label[1]'))).click()
                # Click 'Next' button to continue.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="paymentBtn"]'))).click()
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="paymentProcessBtn"]'))).click()
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="doneBtn"]'))).click()
                sleep(10)
        except ElementNotInteractableException:
            print("ElementNotInteractableException. Exiting...")
            self.driver.close()
            self.driver.quit()
        except NoSuchElementException:
            print("NoSuchElementException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()
        except TimeoutException:
            print("TimeoutException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()


class PortlandGeneralElectric:
    def __init__(self, username, password, sc):
        self.login_timeout = 10
        self.dashboard_timeout = 20
        self.username = username
        self.password = password
        self.psc = sc
        self.individuals = 5
        self.balance = None
        self.pay = None
        self.driver = webdriver.Chrome(drive_path)

    def login(self):
        try:
            self.driver.get('https://new.portlandgeneral.com/auth/sign-in')
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[2]/div[3]/div/div[3]/button'))).click()
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="login-form"]/div[1]/div/div/input'))).send_keys(self.username)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="login-form"]/div[2]/div/div/input'))).send_keys(self.password)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="login-form"]/div[3]/div/div[2]/button/span'))).submit()
        except TimeoutException:
            print("TimeoutException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()

    def get_balance(self):
        try:
            balance = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="full-height-shim"]/div[4]/div/div/div[2]/div/div[3]/div/div/div[4]/div/div[1]/div/div/div/div[2]/div/div[1]/div/div[2]/h2')))
            self.balance = float(balance.text[1:])
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
            print("Extra credit on balance amount. We have paid more than is required on the bill! Excellent :)")
        else:
            print("Your balance is: {}".format(self.balance))
            self.pay = ceil((self.balance / self.individuals) * 100) / 100.0
            print("Each person will pay: {}".format(self.pay))
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
        return 1

    def make_payment(self):
        try:
            # 'Pay Bill' button
            sleep(1)
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="full-height-shim"]/div[4]/div/div/div[2]/div/div[1]/div/button[3]'))).click()
            # 'Credit Card' button
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="scrollable-force-tab-1"]'))).send_keys('\n')
            # 'Pay using billmatrix' button
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="tabpanel-1"]/div/div[3]/button'))).send_keys('\n')

            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.number_of_windows_to_be(2))
            self.driver.switch_to.window(self.driver.window_handles[1])

            # Make payments
            for i in range(0, self.individuals - 4):
                paymentBox = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="PaymentInfoList_0__PaymentAmount"]')))
                paymentBox.clear()
                paymentBox.send_keys(str(5.00))

                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="PaymentInfoList_0__SelectedPaymentCategoryKey"]'))).click()
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="Visa *Chase Nene_0"]'))).click()

                sec_code = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '/html/body/section/form/section/div[2]/div/div/section/div[1]/div[1]/div[4]/div[2]/div/div/div/span[1]/input')))
                sec_code.send_keys(self.psc["Nos"])
                # WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                #     (By.XPATH, '//*[@id="Visa *Chase Nene_0"]'))).click()
                # "Continue" payment, for submitting payment.


            sleep(100)
        except ElementClickInterceptedException:
            print("ElementClickInterceptedException. Exiting...")
            self.driver.close()
            self.driver.quit()
        except ElementNotInteractableException:
            print("ElementNotInteractableException. Exiting...")
            self.driver.close()
            self.driver.quit()
        except NoSuchElementException:
            print("NoSuchElementException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()
        except TimeoutException:
            print("TimeoutException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()




class Xfinity:
    def __init__(self, username, password):
        self.login_timeout = 10
        self.dashboard_timeout = 20
        self.username = username
        self.password = password
        self.individuals = 3
        self.balance = None
        self.pay = None
        self.driver = webdriver.Chrome(drive_path)

    def login(self):
        try:
            self.driver.get('https://customer.xfinity.com/#/billing')
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="user"]'))).send_keys(self.username)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="passwd"]'))).send_keys(self.password)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="sign_in"]'))).submit()
        except TimeoutException:
            print("TimeoutException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()

    def get_balance(self):
        try:
            try:
                WebDriverWait(self.driver, 3).until(EC.alert_is_present(), 'Waiting for pop up')
                alert = self.driver.switch_to.alert
                alert.accept()
                print("Alert accepted")
            except TimeoutException:
                print("Nested TimeoutException occurred. Executing finally block.")
            finally:
                balance = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="page-view"]/section[2]/div/div/div[1]/div[1]/div/div[2]/div[1]/div/div/table/tbody/tr/td[2]/span')))
                self.balance = float(balance.text[1:])
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
            print("Extra credit on balance amount. We have paid more than is required on the bill! Excellent :)")
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
        return 1

    def make_payment(self):
        try:
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="page-view"]/section[2]/div/div/div[1]/div[1]/div/div[2]/div[1]/div/div/div/div[1]/a'))).click()
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="page-main"]/div/div/div/form/div[1]/div/div[2]/div/div[1]/div/div/label'))).click()

            payBox = self.driver.find_element_by_xpath('//*[@id="customAmount"]')
            payBox.clear()
            payBox.send_keys(str('0.01'))

            # Retrieve all cards and eliminate the one that was used for a payment.
            payment1 = self.driver.find_element_by_xpath('//*[@id="page-main"]/div/div/div/form/div[3]/div[2]/div[1]/div/div/div/div/label')
            payment2 = self.driver.find_element_by_xpath('//*[@id="page-main"]/div/div/div/form/div[3]/div[2]/div[2]/div/div/div/div/label')
            payment3 = self.driver.find_element_by_xpath('//*[@id="page-main"]/div/div/div/form/div[3]/div[2]/div[3]/div/div/div/div/label')

            # Store payments that haven't been used.
            cards = [payment1.text.split()[3], payment2.text.split()[3], payment3.text.split()[3]]
            payment1.click()
            cards.remove(payment1.text.split()[3])
            print(cards)
            # Make a payment. Eliminate previously used method. Check if remaining cards are on the webpage.
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="page-main"]/div/div/div/form/div[4]/div[1]/button'))).click()

            # Xfinity tends to not load all stored payments. Find one that we haven't used yet. Eliminate. Repeat.
            while(True):
                try:
                    print("In while loop...")
                    q = input("Do you want to quit loop?").strip()
                    if q == 'Y':
                        break
                    sleep(3)
                    payBox = self.driver.find_element_by_xpath('//*[@id="customAmount"]')
                    payBox.clear()
                    payBox.send_keys(str('0.01'))
                    payment1 = self.driver.find_element_by_xpath('//*[@id="page-main"]/div/div/div/form/div[3]/div[2]/div[1]/div/div/div/div/label')
                    payment2 = self.driver.find_element_by_xpath('//*[@id="page-main"]/div/div/div/form/div[3]/div[2]/div[2]/div/div/div/div/label')
                    payment3 = self.driver.find_element_by_xpath('//*[@id="page-main"]/div/div/div/form/div[3]/div[2]/div[3]/div/div/div/div/label')

                    avail = [payment1.text.split()[3], payment2.text.split()[3], payment3.text.split()[3]]

                except NoSuchElementException:
                    self.driver.refresh()
                    sleep(7)
            sleep(10)
        except NoSuchElementException:
            print("NoSuchElementException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()
        except TimeoutException:
            print("TimeoutException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()


class TMobile:
    def __init__(self, username, password):
        self.login_timeout = 15
        self.dashboard_timeout = 20
        self.username = username
        self.password = password
        self.individuals = 5
        self.balance = None
        self.pay = None
        self.driver = webdriver.Chrome(drive_path)

    def login(self):
        try:
            self.driver.get('https://account.t-mobile.com/signin/v2/')
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="usernameTextBox"]'))).send_keys(self.username)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="lp1-next-btn"]'))).click()
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="passwordTextBox"]'))).send_keys(self.password)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="lp2-login-btn"]'))).submit()
            # balance = WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located((By.CLASS_NAME,'display4 text-center padding-top-xsmall')))
            # print(balance)
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
                WebDriverWait(self.driver, 7).until(EC.alert_is_present(), 'Waiting for pop up')
                alert = self.driver.switch_to.alert
                alert.accept()
                print("Alert accepted")
            except TimeoutException:
                print("Nested TimeoutException occurred. Executing finally block.")
            finally:
                balance = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="maincontent"]/app-home/div/div/div/app-postpaid-home/tmo-billing/div/div[1]/div/div[3]/div[2]/span')))
                self.balance = float(balance.text.strip().replace(" ", "")[1:])
                print(self.balance)
                sleep(10)
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
        return 1

    def make_payment(self):
        pass


def call_choices(choices):
    for choice in choices:
        if choice == 1:
            # Pay City of Salem account.
            c = CityOfSalem(cuser, cpass)
            c.login()
            c.get_balance()
            c.validate()
        if choice == 2:
            # Pay Suburban Garbage Service account.
            s = SuburbanGarbage(suser, spass)
            s.login()
            s.get_balance()
            s.validate()
        if choice == 3:
            # Pay Portland General Electric account.
            p = PortlandGeneralElectric(puser, ppass, psc)
            p.login()
            p.get_balance()
            p.validate()
        if choice == 4:
            # Pay Xfinity account.
            x = Xfinity(xuser, xpass)
            x.login()
            x.get_balance()
            x.validate()
        if choice == 5:
            # Pay T-Mobile account.
            t = TMobile(tuser, tpass)
            t.login()
            t.get_balance()
            # t.make_payment()


def main():
    print("\n\nWhat do you want to pay?\n")
    print("    1) City of Salem    (Water Bill)")
    print("    2) Suburban Garbage (Garbage Bill)")
    print("    3) PGE              (Electric Bill)")
    print("    4) Xfinity          (Internet Bill)")
    print("    5) T-Mobile         (Phone Bill)\n")

    while True:
        choices = input("Select your options. (Example: 1 3 4): ").split()
        try:
            choices = [int(choice) for choice in choices]
        except ValueError:
            print("Unable to convert input to integers")
            continue

        if all(0 < choice <= 5 for choice in choices):
            print("Thanks!")
            call_choices(choices)
            break
        else:
            print("Try again!")
            continue


if __name__ == '__main__':
    main()

