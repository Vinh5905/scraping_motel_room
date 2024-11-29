from selenium import webdriver
from bs4 import BeautifulSoup
from pathlib import Path

'''
CHÚ Ý :
    * Chotot
        - Với page_source của page (để get link) thì xử lí chưa ổn, vẫn còn bị nhiều cái chưa xem rõ ràng được
        - Chỉ sử dụng với các page product
'''

def format_html(link):
    path_html = Path('./check_page_source/formatted.html')

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

    with open(path_html, 'w') as file:
        # print("COME HERE TO OPEN FILE")
        file.write(page_source_formatted)

    driver.quit()

if __name__ == '__main__':
    format_html('https://www.nhatot.com/thue-phong-tro-quan-8-tp-ho-chi-minh/68268900.htm#px=SR-stickyad-[PO-1][PL-top]')