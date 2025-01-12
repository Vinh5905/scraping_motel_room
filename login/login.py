import pickle
from shared.globals import COOKIES_PATH
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

class Login:
    def __init__(self, driver):
        self.__driver = driver
        pass

    def prepare_cookies(self):
        login_button = self.__driver.find_element(By.CSS_SELECTOR, '#kct_login')
        ActionChains(self.__driver) \
            .click(login_button) \
            .perform()

        wait = WebDriverWait(self.__driver, 20)

        iframe_login_popup = wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, 'iframe[src="https://batdongsan.com.vn/sellernet/internal-sign-in"]'))

        self.__driver.switch_to.frame(iframe_login_popup)
        gg_login = wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, 'button[data-tracking-id="click-sign-in"][data-tracking-label="type=Google"]'))

        original_window = self.__driver.current_window_handle        
        ActionChains(self.__driver) \
            .click(gg_login) \
            .perform() 

        while True:
            print('CAN I START NOW ??')
            print('[Y] Yes     [N] No')
            wait_to_login_success = input('Answer: ')
            if wait_to_login_success.lower() == 'y' or wait_to_login_success.lower() == 'yes':
                break
        
        self.__driver.switch_to.window(original_window) # Cung ko nhat thiet phai doi lại origin để lấy cookies, vì selenium chỉ đổi DOM thôi
        # cookies = self.__driver.get_cookies()
        # print(cookies)
        # with open(COOKIES_PATH, 'wb') as file:
        #     pickle.dump(cookies, file)
            
        self.__driver.refresh()


# AUTO LOGIN (failed)
        # email_input = driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        # button_from_email_to_next = driver.find_element(By.CSS_SELECTOR, 'button.nCP5yc')

        # ActionChains(driver) \
        #     .send_keys_to_element(email_input, email_name) \
        #     .pause(2) \
        #     .click(button_from_email_to_next) \
        #     .perform()

        # password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        # button_from_password_to_next = driver.find_element(By.CSS_SELECTOR, 'button.nCP5yc')

        # ActionChains(driver) \
        #     .send_keys_to_element(password_input, password) \
        #     .pause(2) \
        #     .click(button_from_password_to_next) \
        #     .perform()

        # time.sleep(2)
        # button.click()
        # time.sleep(10)
        # print(driver.window_handles)
        # driver.switch_to.default_content()
