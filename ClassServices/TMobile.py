from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from time import sleep
from math import ceil


class TMobile:
    def __init__(self, path, options, username, password):
        self.username = username
        self.password = password
        self.individuals = 6
        self.balance = None
        self.service = None
        self.pay = None
        self.phones = None
        self.pay_history = []
        self.add = 0.0
        self.elements = None
        self.login_timeout = 60
        self.dashboard_timeout = 20
        self.payment_timeout = 2
        self.path = path
        self.options = options
        self.driver = None

    def init_driver(self):
        self.driver = webdriver.Chrome(self.path, options=self.options)

    def display_info(self):
        print("    Username: " + self.username)
        print("    Individuals: " + str(self.individuals))
        print("    Balance: " + str(self.balance))
        print("    Service: " + str(self.service))
        print("    Pay: " + str(self.pay))
        print("    Phones: " + str(self.phones))
        print("    Pay History: " + str(self.pay_history) + "\n")

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
                        self.service = float(input("\nEnter service amount (decimal): ").strip())
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

    # T-mobile prevents consecutive payments of the same amount within 24 hours.
    #   Check if we are about to make a duplicate charge. Add a penny to the current payment to avoid this.
    # Arguments: the pay (the current payment to be made)
    # Returns:
    #   1) the pay if it is the first charge
    #   2) the pay if there are no duplicates
    #   3) the pay plus an added penny if a duplicate is found
    def equal_to_prev(self, pay):
        if self.pay_history:
            if pay in self.pay_history:
                self.add += 0.01
                curr_val = round(pay + self.add, 2)
                self.pay_history.append(curr_val)
                return curr_val
            else:
                return pay
        else:
            self.pay_history = []
            self.pay_history.append(pay)
            return pay

    def login(self):
        try:
            self.driver.get('https://account.t-mobile.com/signin/v2/?redirect_uri=https:%2F%2Fwww.t-mobile.com%2Fsignin&scope=TMO_ID_profile%20associated_lines%20billing_information%20associated_billing_accounts%20extended_lines%20token%20openid&client_id=MYTMO&access_type=ONLINE&response_type=code&approval_prompt=auto&device_type=desktop&prompt=select_account')
            while True:
                confirm = input("Entered user info? [Y/N]: ")
                if confirm in ["Y", "y"]:
                    break
                elif confirm in ["N", "n"]:
                    print("Exiting and returning...")
                    return None
                else:
                    print("Please enter a valid response.")
                    continue
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
                balance = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="margin-bottom-xs margin-top-0 heading-4 ng-star-inserted"]')))
                self.balance = float(balance.text.strip().replace(" ", "")[1:])
                print(self.balance)
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

    def set_elements(self):
        WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'button[class="bb-type-selector bb-line-selector col-6 col-lg-3"]'))).click()
        # Retrieve all the elements associated with each phone line.
        self.elements = WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div[class="row row-details"]')))
        print("Retrieved all elements associated with each phone line.")

    def set_service_cost(self):
        # Retrieve the balance for the service plan for all phones.
        self.service = float(self.elements[1].text.split()[1][1:])
        print("")
        print("Retrieved the service amount for all phone lines.")

    def set_line_costs(self):
        # Initialize a dict for all phone lines => {"Name": $0.0}
        self.phones = dict((e.text.split()[0], 0.0) for e in self.elements[2:])
        print("Initialized dict for all phone lines.")
        # Retrieve quantities for each phone line in "view by line"
        for e in self.elements[2:]:
            line = e.text.split()
            try:
                name, amount = line[0], float(line[1][1:])
            except ValueError as e:
                name, amount = line[0], float(line[2][1:])
            self.phones[name] += round(ceil(amount * 100) / 100.0, 2)
        print("Filled dictionary with all phone lines and their associated values.")
        print(self.phones)
        self.pay = ceil((self.service / self.individuals) * 100) / 100.0
        print("Each individual will pay ${} in service fees.".format(self.pay))

    def fix_line_costs(self):
        for i, (k, v) in enumerate(self.phones.items()):
            # This person pays for two service lines.
            if i == 3:
                self.phones[k] += self.pay * 2
                self.phones[k] += list(self.phones.values())[-1]
            # This person pays for two accounts, including insurance.
            elif i == 4:
                self.phones[k] += self.pay
                self.phones[k] += list(self.phones.values())[2]
            else:
                self.phones[k] += self.pay
            self.phones[k] = round(self.phones[k], 2)
            ret = self.equal_to_prev(self.phones[k])
            self.phones[k] = ret
            if i != 2 and i != 5:
                print("{} will pay a total of ${}".format(k, self.phones[k]))
        del self.phones[list(self.phones.keys())[2]]
        del self.phones[list(self.phones.keys())[-1]]

    def gather_bill_info(self):
        try:
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[class="mat-focus-indicator cta-button mat-stroked-button mat-button-base mat-primary ng-star-inserted"]'))).click()
            print("Clicked on \"View Bill\"")
            print("Setting elements...")
            self.set_elements()
            print("Setting service costs...")
            self.set_service_cost()
            print("Setting line costs...")
            self.set_line_costs()
            print("Fixing line costs...")
            self.fix_line_costs()
            print("Total: {}".format(round(sum([i for i in list(self.phones.values())]), 2)))
            # Ask for further confirmation
            while True:
                confirm = input("Make payments? [Y/N]: ").strip()
                if confirm in ["Y", "y"]:
                    return self.make_payments()
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

    def make_payments(self):
        try:
            flag = False
            WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[aria-label="Clickable Make a payment"]'))).click()
            for i, (k, v) in enumerate(self.phones.items()):
                print("\n\nCurrently on {}'s phone to pay {}.".format(k, v))
                if not flag:
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
                amount = str(v)
                amount_box.send_keys(amount)
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
                print("Payment amount of {}.".format(amount))
                while True:
                    confirm = input("Confirm? [Y/N]: ").strip()
                    if confirm in ["Y", "y"]:
                        print("Confirming payment...")
                        break
                    elif confirm in ["N", "n"]:
                        print("Continuing next payment.")
                        continue
                    else:
                        print("Please try a valid response.")
                # Retrieve current_url before making making a payment. This is so that the page finishes loading.
                current_url = self.driver.current_url
                # Confirm payment => "Agree and Submit" button.
                WebDriverWait(self.driver, self.dashboard_timeout).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button[class="btn btn-primary button-title PrimaryCTA glueButton '
                                      'gluePull-left-sm"]'))).click()
                sleep(1)
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
