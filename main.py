from secrets import cuser, cpass, suser, spass, puser, ppass, psc, xuser, xpass, tuser, tpass
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, \
    ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from decimal import Decimal, getcontext
from selenium import webdriver
from time import sleep
from math import ceil

getcontext().prec = 2
chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument('--log-level=3')
drive_path = './chromedriver.exe'


class CityOfSalem:
    def __init__(self, username, password):
        self.login_timeout = 10
        self.dashboard_timeout = 20
        self.username = username
        self.password = password
        self.individuals = 6
        self.balance = None
        self.pay = None
        self.driver = webdriver.Chrome(drive_path, options=chrome_options)

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
                if i == 3:
                    pay_box.send_keys(str(self.pay * 2))
                else:
                    pay_box.send_keys(str(self.pay))
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
        self.individuals = 6
        self.balance = None
        self.pay = None
        self.driver = webdriver.Chrome(drive_path, options=chrome_options)

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
            # We want to start with index 1 up to self.individuals
            for i in range(1, self.individuals):
                # Navigate to payment page.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="payNowLink"]'))).click()
                # Retrieve payment box. Clear and add quantity.
                payment_box = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="amount"]')))
                payment_box.clear()
                if i == 5:
                    payment_box.send_keys(str(self.pay * 2))
                else:
                    payment_box.send_keys(str(self.pay))
                # Select which payment option to use => Pay Now
                payment_option = Select(WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="paymentTime"]'))))
                payment_option.select_by_index(1)
                # Choose which payment method to use.
                payment_type = Select(WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="paymentOption"]'))))
                payment_type.select_by_index(i)
                sleep(7)
                # Click 'Yes, I agree' button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'label[for="agreeY"]'))).click()
                # Click 'Next' button to continue.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="paymentBtn"]'))).click()
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


class PortlandGeneralElectric:
    def __init__(self, username, password, sc):
        self.login_timeout = 10
        self.dashboard_timeout = 60
        self.username = username
        self.password = password
        self.psc = sc
        self.individuals = 6
        self.balance = None
        self.pay = None
        self.driver = webdriver.Chrome(drive_path, options=chrome_options)

    def login(self):
        try:
            self.driver.get('https://new.portlandgeneral.com/auth/sign-in')
            try:
                ok_button = WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[class="MuiButtonBase-root MuiButton-root MuiButton-contained '
                                  'MuiButton-containedPrimary"][type="button"]')))
                ok_button.click()
            except NoSuchElementException as e:
                print("No \"OK\" button found.")
                print(e)
            except ElementClickInterceptedException as e:
                print("Could not click on element. Intercepted.")
                print(e)
            except ElementNotInteractableException as e:
                print("Element was not interactable.")
                print(e)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[name="email"][type="email"]'))).submit()
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[name="email"][type="email"]'))).send_keys(self.username)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[name="password"][type="password"]'))).send_keys(self.password)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[class="MuiButtonBase-root MuiButton-root MuiButton-contained jss7 jss94 '
                                  'jss76 MuiButton-containedPrimary"][type="submit"]'))).submit()
        except Exception as e:
            print("Error occurred. Exiting...")
            print(e)
            self.driver.close()
            self.driver.quit()

    def get_balance(self):
        try:
            balance = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'h2[class="MuiTypography-root jss145 MuiTypography-h2"]')))
            self.balance = float(balance.text[1:])
        except Exception as e:
            print("Exception occurred while retrieving balance. Exiting...")
            print(e)
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
            # 'Pay Bill' button.
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[class="MuiButtonBase-root MuiButton-root MuiButton-contained jss157 jss166 '
                                  'MuiButton-containedPrimary MuiButton-fullWidth"][type="button"]'))).send_keys('\n')
            # 'Credit Card' button.
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[id="scrollable-force-tab-1"][type="button"]'))).send_keys('\n')
            # 'Pay using billmatrix' button.
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[data-testid="pay-bill-matrix-button"][type="button"]'))).send_keys('\n')
            # Switch over tabs.
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.number_of_windows_to_be(2))
            self.driver.switch_to.window(self.driver.window_handles[1])
            # Select payment categories.
            payment_methods = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="PaymentInfoList_0__SelectedPaymentCategoryKey"]')))
            payment_methods.click()

            # Retrieve wallet.
            wallet = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="Ul_0"]')))

            # Get list of cards
            cards = []
            for item in wallet.find_elements_by_tag_name('li')[0:5]:
                cards.append(item.find_element_by_tag_name('a').get_attribute('id').strip())

            # Get list of names
            names = list(self.psc.keys())
            # Raise/close drop down menu for "Using" box to start for loop properly. Otherwise, drop down menu
            # remains open.
            payment_methods.click()

            # Make payments for all cards stored in wallet.
            card_info = dict(zip(names, cards))
            for i, (k, v) in enumerate(card_info.items()):
                # Click on payment method box => "Using" box to open drop down menu.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="PaymentInfoList_0__SelectedPaymentCategoryKey"]'))).click()
                # Select which card payment method to use.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="' + v + '"]'))).click()
                # Retrieve payment box => "Pay $" box.
                pay_amount = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="PaymentInfoList_0__PaymentAmount"]')))
                pay_amount.clear()
                if i == 4:
                    pay_amount.send_keys('{:,.2f}'.format(self.pay * 2.0))
                else:
                    pay_amount.send_keys('{:,.2f}'.format(self.pay))
                # Retrieve security code box => "Security Code" box.
                security_code = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="PaymentInfoList_0__CardWallet_SecurityCode"]')))
                # Enter the security code given self.psc imported from secrets.py
                security_code.send_keys(self.psc[k])
                # 'Continue' button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="btnPayNow_Continue"]'))).send_keys('\n')
                # Retrieve current url before submitting payment, so that we wait for confirmation page to finish and be
                # consistent with the for loop. PGE has a different view of the page if we remain on BillMatrix page.
                current_url = self.driver.current_url
                # 'Pay' button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="btnReview_Pay"]'))).send_keys('\n')
                # Wait until confirmation page is done loading before starting another payment.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.url_changes(current_url))
                # Return to the payment information page to process the next payment.
                self.driver.get('https://webpayments.billmatrix.com/PGEfp/Payment/paymentinformation')
        except Exception as e:
            print("Error occurred.\nQuiting driver...")
            print("Error:\n{}".format(e))
        return 1


class Xfinity:
    def __init__(self, username, password):
        self.login_timeout = 10
        self.dashboard_timeout = 25
        self.username = username
        self.password = password
        self.individuals = 3
        self.balance = None
        self.pay = None
        self.driver = webdriver.Chrome(drive_path, options=chrome_options)

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
                    (By.CSS_SELECTOR, 'span[class="price price--fancy mb0"][price="billOverviewBalanceDue"]')))
                self.balance = float(balance.text[1:])
        except NoSuchElementException:
            print("NoSuchElementException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()
        except TimeoutException:
            print("TimeoutException occurred. Exiting...")
            self.driver.close()
            self.driver.quit()

    def validate(self):
        self.balance = 69.99
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
                (By.CSS_SELECTOR, 'a[class="button button--primary"][ng-href="https://payments.xfinity.com/new"]'))).click()
            # Retrieve all cards going to be used.
            card_group = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'span[class="payment-instrument__text"]')))
            card_elements = [item for item in card_group]
            card_elements = card_elements
            for item in card_elements:
                print(item.text)
            sleep(3)
            for item in card_elements:
                payment_box = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="customAmount"]')))
                print("Using card: " + str(item.text))
                payment_box.send_keys(Keys.CONTROL, 'a')
                payment_box.send_keys(Keys.BACKSPACE)
                payment_box.send_keys(str(self.pay))
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'label[class="form-control__label"][for="paymentAmountOptionUserDefined"'))).click()
                # Find and click on payment method given current item in card_elements
                curr_element = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), '" + str(item.text) + "')]")))
                # Select that payment method.
                curr_element.click()
                # Navigate to confirmation page => 'Continue' button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button[class="button button--primary"][type="submit"]'))).submit()
                # Confirm payment => 'Submit Payment' button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button[class="button button--primary"][type="submit"]'))).submit()
                # Make a new payment => 'New Payment'
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


class TMobile:
    def __init__(self, username, password):
        self.login_timeout = 15
        self.dashboard_timeout = 20
        self.payment_timeout = 2
        self.username = username
        self.password = password
        self.individuals = 6
        self.balance = None
        self.service = None
        self.phones = None
        self.pay = None
        self.driver = webdriver.Chrome(drive_path, options=chrome_options)

    def login(self):
        try:
            self.driver.get('https://account.t-mobile.com/signin/v2/')
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="usernameTextBox"]'))).send_keys(self.username)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="lp1-next-btn"]'))).click()
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="passwordTextBox"]'))).send_keys(self.password)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="lp2-login-btn"]'))).submit()
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
                return 1
        except Exception as e:
            print("Error occurred attempting to retrieve balance. Exiting...")
            print("Error: {}".format(e))
            self.driver.close()
            self.driver.quit()
            return 0

    def validate(self):
        if self.balance == 0.0:
            print("No balance to pay")
        elif self.balance < 0.0:
            print("Extra credit on balance amount. We have paid more than is required on the bill! Excellent :)")
        else:
            print("Your balance is: {}".format(self.balance))
            while True:
                confirm = input("Continue? [Y/N]: ").strip()
                if confirm in ["Y", "y"]:
                    return self.gather_bill_info()
                elif confirm in ["N", "n"]:
                    print("No payment was made.")
                    break
                else:
                    print("No valid response. Try again.")
                    continue
        return 0

    def gather_bill_info(self):
        try:
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[aria-label="View bill"]'))).click()
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[class="bb-type-selector bb-line-selector col-6 col-lg-3"]'))).click()
            # Retrieve all the elements associated with each phone line.
            elements = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'div[class="offscreen"]')))
            # Retrieve the balance for the service plan for all phones.
            self.service = float(elements[1].text.split()[1][1:])
            print(self.service)
            # Initialize a dict for all phone lines => {"Name": $}
            self.phones = dict((e.text.split()[0], 0.0) for e in elements[2:])
            # Retrieve quantities for each phone line
            for e in elements[2:]:
                line = e.text.split()
                name, amount = line[0], float(line[1][1:])
                self.phones[name] += ceil(amount * 100) / 100.0
                self.phones[name] = round(self.phones[name], 2)
            print(self.phones)
            self.pay = ceil((self.service / self.individuals) * 100) / 100.0
            print("Each individual will pay ${} in service fees.".format(self.pay))
            total = 0.0
            for i, (k, v) in enumerate(self.phones.items()):
                if i == 3:
                    self.phones[k] += (self.pay * 2)
                    self.phones[k] = round(self.phones[k], 2)
                elif i == 4:
                    self.phones[k] += self.pay
                    self.phones[k] += list(self.phones.values())[2]
                    self.phones[k] = round(self.phones[k], 2)
                else:
                    self.phones[k] += self.pay
                    self.phones[k] = round(self.phones[k], 2)
                if i != 2:
                    print("{} will pay a total of ${}".format(k, self.phones[k]))
            del self.phones[list(self.phones.keys())[2]]
            print("Total: {}".format(round(sum([i for i in list(self.phones.values())]), 2)))
            # Ask for further confirmation
            while True:
                confirm = input("Make payments? [Y/N]: ").strip()
                if confirm in ["Y", "y"]:
                    return self.make_payment()
                elif confirm in ["N", "n"]:
                    print("No payment was made.")
                    break
                else:
                    print("No valid response. Try again.")
                    continue
            return 0
        except Exception as e:
            print("Error occured while attempting to gather bill info.")
            print("Error: {}".format(e))
            self.driver.close()
            self.driver.quit()
            return 0

    def make_payment(self):
        try:
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[aria-label="Clickable Make a payment"]'))).click()
            for i, (k, v) in enumerate(self.phones.items()):
                print("Currently on {}'s phone to pay {}.".format(k, v))
                sleep(5)
                # Click on amount => "Amount" div.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'i[class="fa fa-angle-right caretLeftIcon fa-rightIcon text-black text-bold '
                                      'fa-lg arrow-padding-left line-ht"]'))).click()
                # Retrieve the amount box to add quantity => "Other" box.
                amount_box = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[id="otherAmount"]')))
                # Clear amount box.
                amount_box.clear()
                # Send the quantity for the current phone line.
                amount_box.send_keys(str(v))
                try:
                    # Click to update quantity for amount box => "Update" button.
                    WebDriverWait(self.driver, self.payment_timeout).until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'button[ng-click="vm.updateAmount()"]'))).click()
                except Exception as e:
                    print("Error: {}".format(e))
                    print("Possibly amount remained the same. Cancelling...")
                    WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'button[aria-label="Cancel Label"]'))).click()
                # Click on payment method => "Payment method" div.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'i[aria-label="change payment method active clickable blade"]'))).click()
                # Click on the appropriate method of payment.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'span[aria-label="' + str(k) + '"]'))).click()
                # Retrieve button to confirm payment method => "Select Payment Method" button.
                try:
                    WebDriverWait(self.driver, self.payment_timeout).until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'button[class="PrimaryCTA w-100 full-btn-width float-md-left '
                                              'float-lg-left '
                                              'float-xl-left"]'))).click()
                except Exception as e:
                    print("Error: {}".format(e))
                    print("Possibly method is already selected. Cancelling...")
                    WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'button[class="SecondaryCTA blackCTA w-100 full-btn-width float-md-right '
                                          'float-lg-right float-xl-right"]'))).click()
                # Retrieve current_url before making making a payment. This is so that the page finishes loading.
                current_url = self.driver.current_url
                # Confirm payment => "Agree and Submit" button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button[class="btn btn-primary button-title PrimaryCTA glueButton '
                                      'gluePull-left-sm"]'))).click()
                # Wait until confirmation page is done loading before starting another payment.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.url_changes(current_url))
                print("Confirmed for {} in amount ${}.".format(k, v))
                # Return to the payment information page to process the next payment.
                self.driver.get("https://my.t-mobile.com/onetimepayment")
            return 1
        except Exception as e:
            print("Error occurred while attempting to gather bill info.")
            print("Error: {}".format(e))
            self.driver.close()
            self.driver.quit()
            return 0

    def close(self):
        print("Exiting T-Mobile driver.")
        self.driver.close()
        self.driver.quit()


def call_choices(choices):
    for choice in choices:
        # City of Salem.
        if choice == 1:
            c = CityOfSalem(cuser, cpass)
            c.login()
            c.get_balance()
            c.validate()
        # Suburban Garbage Service.
        if choice == 2:
            s = SuburbanGarbage(suser, spass)
            s.login()
            s.get_balance()
            s.validate()
        # Portland General Electric.
        if choice == 3:
            p = PortlandGeneralElectric(puser, ppass, psc)
            p.login()
            p.get_balance()
            p.validate()
        # Xfinity.
        if choice == 4:
            x = Xfinity(xuser, xpass)
            x.login()
            x.get_balance()
            if x.validate():
                x.close()
        # T-Mobile.
        if choice == 5:
            t = TMobile(tuser, tpass)
            t.login()
            if t.get_balance():
                if t.validate():
                    t.close()


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

