from selenium import webdriver
from bs4 import BeautifulSoup
from pathlib import Path
from shared.globals import CHECK_FORMATTED_PAGE_SOURCE_PATH

'''
CHÚ Ý :
    * Chotot
        - Với page_source của page (để get link) thì xử lí chưa ổn, vẫn còn bị nhiều cái chưa xem rõ ràng được
        - Chỉ sử dụng với các page product
'''

def format_html_link(link):
    # The website is possibly blocking or restricting the user agent for selenium. (sometime need)
    user_agent_string = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"user-agent={user_agent_string}")
    # print("OPTIONS DONE")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)

    driver.get(link)
    # print("GET LINK DONE")

    page_source_raw = driver.page_source
    # print("GET PAGE SOURCE DONE")

    soup = BeautifulSoup(page_source_raw, 'html.parser')

    page_source_formatted = soup.prettify()
    # print("PRETTIFY DONE")

    with open(CHECK_FORMATTED_PAGE_SOURCE_PATH, 'w') as file:
        print("COME HERE TO OPEN FILE")
        file.write(page_source_formatted)

    driver.quit()

def format_html_page_source(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')

    page_source_formatted = soup.prettify()
    # print("PRETTIFY DONE")

    with open(CHECK_FORMATTED_PAGE_SOURCE_PATH, 'w') as file:
        file.write(page_source_formatted)