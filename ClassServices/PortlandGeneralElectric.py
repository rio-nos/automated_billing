from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from math import ceil


class PortlandGeneralElectric:
    def __init__(self, path, options, username, password, sc):
        self.username = username
        self.password = password
        self.individuals = 6
        self.balance = None
        self.pay = None
        self.sc = sc
        self.login_timeout = 10
        self.dashboard_timeout = 60
        self.path = path
        self.options = options
        self.driver = None

    def init_driver(self):
        self.driver = webdriver.Chrome(self.path, options=self.options)

    def display_info(self):
        print("    Username: " + self.username)
        print("    Individuals: " + str(self.individuals))
        print("    Balance: " + str(self.balance))
        print("    Pay: " + str(self.pay))

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
            self.driver.get('https://new.portlandgeneral.com/auth/sign-in')
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[name="email"][type="email"]'))).send_keys(self.username)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[name="password"][type="password"]'))).send_keys(self.password)
            WebDriverWait(self.driver, self.login_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[id="sign-in-submit-btn"][type="submit"]'))).submit()
        except Exception as e:
            print("Error occurred. Exiting...")
            print(e)
            self.driver.close()
            self.driver.quit()

    def get_balance(self):
        try:
            print("Retrieving balance")
            balance = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'h2[class="MuiTypography-root jss149 MuiTypography-h2"]')))
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
                (By.CSS_SELECTOR, 'button[class="MuiButtonBase-root MuiButton-root MuiButton-contained jss10 jss167 MuiButton-containedPrimary MuiButton-fullWidth"][type="button"]'))).send_keys('\n')
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
            names = list(self.sc.keys())
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
                amount = 0
                if i == 4:
                    amount = '{:,.2f}'.format(self.pay*2.0)
                    pay_amount.send_keys(amount)
                else:
                    amount = '{:,.2f}'.format(self.pay)
                    pay_amount.send_keys(amount)
                # Retrieve security code box => "Security Code" box.
                security_code = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="PaymentInfoList_0__CardWallet_SecurityCode"]')))
                # Enter the security code given self.psc imported from secrets.py
                security_code.send_keys(self.psc[k])
                print("Payment amount of {}.".format(amount))
                while True:
                    confirm = input("Confirm? [Y/N]: ").strip()
                    if confirm in ["Y", "y"]:
                        print("Confirming payment...")
                        break
                    elif confirm in ["N", "n"]:
                        print("Continuing next payment.")
                        self.driver.get('https://webpayments.billmatrix.com/PGEfp/Payment/paymentinformation')
                        continue
                    else:
                        print("Please try a valid response.")
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
