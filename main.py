from selenium.webdriver.chrome.options import Options
from ClassServices import CityOfSalem, SuburbanGarbage, PortlandGeneralElectric, Xfinity, TMobile
from secrets import cuser, cpass, suser, spass, puser, ppass, psc, xuser, xpass, tuser, tpass

options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('--log-level=3')
drive_path = './chromedriver.exe'


def call_choices(services):
    for service in services:
        # City of Salem.
        if service == 1:
            c = CityOfSalem.CityOfSalem(drive_path, options, cuser, cpass)
            c.init_driver()
            c.prompt_user()
            c.login()
            c.get_balance()
            c.validate()
        # Suburban Garbage Service.
        if service == 2:
            s = SuburbanGarbage.SuburbanGarbage(drive_path, options, suser, spass)
            s.init_driver()
            s.prompt_user()
            s.login()
            s.get_balance()
            s.validate()
        # Portland General Electric.
        if service == 3:
            p = PortlandGeneralElectric.PortlandGeneralElectric(drive_path, options, puser, ppass, psc)
            p.init_driver()
            p.prompt_user()
            p.login()
            p.get_balance()
            p.validate()
        # Xfinity.
        if service == 4:
            x = Xfinity.Xfinity(drive_path, options, xuser, xpass)
            x.init_driver()
            x.login()
            x.get_balance()
            if x.prompt_user():
                x.validate()
                x.close()
                continue
            else:
                x.validate()
                x.close()
                continue
        # T-Mobile.
        if service == 5:
            t = TMobile.TMobile(drive_path, options, tuser, tpass)
            t.init_driver()
            t.login()
            t.get_balance()
            t.validate()
            t.close()


def main():
    print("\n\nSelect the services you want to pay.\n")
    print("    1) City of Salem    (Water Bill)")
    print("    2) Suburban Garbage (Garbage Bill)")
    print("    3) PGE              (Electric Bill)")
    print("    4) Xfinity          (Internet Bill)")
    print("    5) T-Mobile         (Phone Bill)\n")
    while True:
        try:
            services = input("Enter services (Ex., 2 3 5): ").strip().split()
            services = [int(service) for service in services]
            if all(0 < service <= 5 for service in services):
                print("Calling choices")
                call_choices(services)
                break
            else:
                print("\nTry again.")
                continue
        except ValueError:
            print("Error: unable to convert input to integer."
                  "\nPlease try again!")
            continue


if __name__ == '__main__':
    main()

