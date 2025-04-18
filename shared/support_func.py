import ast
import random
import re
import json
import pickle
import base64
import os
from pathlib import Path
import time
import dotenv
import threading
# from bs4 import BeautifulSoup
# from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from shared.globals import TERMINAL_WIDTH, PROXIES_LIST, SAVE_DATA_PATH, CHECKPOINTS_PATH, COOKIES_PATH, DRIVER_PATH, LOCK_LINK_LIST, UPDATE_TIME, CHECKPOINTS_PATH_TEST
from login.login import Login_Batdongsan, Login_Chotot
from msgraph_onedrive.operations import upload_file, upload_img, create_folder, search_file_id, download_file
from msgraph_onedrive.syn import update_crawl_info, update_link_list, update_extract_info
from shared.colorful import print_banner_colored

def string_to_dict(text: str):
    # Erase indent start and end of string (if not -> IndentationError: unexpected indent)
    text = text.strip()
    # Some marks are wrong
    text = text.replace('`', "'").replace('"', "'")
    # Key need to be in quotes
    text = re.sub(r'(\w+): ', r"'\1': ", text)
    # Change to dict
    value_dict_type = ast.literal_eval(text)

    return value_dict_type

def base64_to_binary(base64_list):
    binary_list = []

    for index in range(len(base64_list)):
        if base64_list[index].lstrip().startswith('data:image'):
            base64_data = base64_list[index].split(',')[1]
        else:
            base64_data = base64_list[index]
        
        binary_data = base64.b64decode(base64_data)

        binary_list.append(binary_data)
    
    return binary_list


def reset_previous_crawl(PATH):
    try:
        with open(PATH['CRAWL'], 'r') as file:
            previous_multi_crawl = json.load(file)

        for index in range(len(previous_multi_crawl['running_thread'])):
            previous_multi_crawl['running_thread'][index]['isCrawling'] = False

        with open(PATH['CRAWL'], 'w') as file:
            json.dump(previous_multi_crawl, file)

    except:
        return        


def return_PATH(web, test):
    web = web.upper()

    if web in ('BATDONGSAN', 'CHOTOT'):
        PATH = CHECKPOINTS_PATH_TEST[web] if test else CHECKPOINTS_PATH[web]
        return PATH 
    else:
        raise ValueError('WEB is not in value range (BATDONGSAN - CHOTOT)')
    

def get_proxy_random(proxies_list_custom = None): 
    # If not have custom, get globals value
    proxies = proxies_list_custom or PROXIES_LIST

    proxy_stt = random.randrange(0, len(proxies))

    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': proxies[proxy_stt],
        # 'sslProxy': proxies[proxy_stt]
    })

    return proxy


def get_new_driver(driver_num = 1, chorme_options_custom = None, security=False):
    if not security:
        # If not have custom then use default self-config
        chrome_options = chorme_options_custom or webdriver.ChromeOptions()
        # chrome_service = Service('/Users/hoangvinh/OneDrive/Workspace/Support/Driver/chrome-headless-shell-mac-x64/chrome-headless-shell')
        chrome_service = Service(DRIVER_PATH(driver_num))

        if not chorme_options_custom:
            user_agent_string = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            chrome_options.add_argument(f"user-agent={user_agent_string}")
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument("--start-maximized")
            # chrome_options.add_argument('--ignore-ssl-errors=yes')
            # chrome_options.add_argument('--ignore-certificate-errors')
            # chrome_options.add_argument('--headless')
            # chrome_options.add_argument("--incognito")
            # chrome_options.proxy = get_proxy_random()
        driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    else:
        chrome_options = webdriver.ChromeOptions()
        user_agent_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        chrome_options.add_argument(f"user-agent={user_agent_string}")
        # chrome_options.add_argument('--disable-web-security')
        # chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)

    return driver


def get_link_page(base_link, page_num, PATH):
    match PATH['NAME']:
        case 'BATDONGSAN':
            if page_num == 1: 
                # Keep origin because page 1 is as same as base link
                return base_link
            else: 
                return f'{base_link}/p{page_num}'
        case 'CHOTOT':
            if page_num == 1: 
                # Keep origin because page 1 is as same as base link
                return base_link
            else: 
                return f'{base_link}?page={page_num}'
    
    raise ValueError('URL của link không nằm trong get_link_page')


def get_pos_start_crawl(PATH):
    previous_crawl = None

    try:
        with open(PATH['CRAWL'], 'r') as file:
            previous_crawl = json.load(file)
    except:
        with open(PATH['CRAWL'], 'w') as file:
            page_default = 1
            link_default = 0

            previous_crawl = {   
                'next_page': page_default + 1,
                'running_thread': [
                    {
                        "page": page_default,
                        "link": link_default,
                        "isCrawling": True
                    }
                ]
            }

            json.dump(previous_crawl, file)
            return [1, 0]
    
    for index, item in enumerate(previous_crawl['running_thread']):
        if not item['isCrawling']:
            page_num = item['page']
            link_num = item['link']

            previous_crawl['running_thread'][index]['isCrawling'] = True

            with open(PATH['CRAWL'], 'w') as file:
                json.dump(previous_crawl, file)
            return [page_num, link_num]
    
    # If not have any False
    new_page_crawling = {
        'page': previous_crawl['next_page'],
        'link': 0,
        'isCrawling': True
    }

    new_crawl = {
        'next_page': previous_crawl['next_page'] + 1,
        'running_thread': [
            *previous_crawl['running_thread'],
            new_page_crawling
        ]
    }

    with open(PATH['CRAWL'], 'w') as file:
        json.dump(new_crawl, file)

    return [new_page_crawling['page'], new_page_crawling['link']]


def is_login(driver, PATH):
    match PATH['NAME']:
        case 'BATDONGSAN':
            try:
                driver.find_element(By.CSS_SELECTOR, '#kct_login')
                return False
            except:
                # print_banner_colored('Chưa login', 'wait')
                return True
        case 'CHOTOT':
            try:
                driver.find_element(By.CSS_SELECTOR, '.ct_lr__p1thhhsi')
                return False
            except:
                # print_banner_colored('Chưa login', 'wait')
                return True

def change_cookies_driver(driver, PATH):
    try:
        print_banner_colored('Tìm và bắt đầu load cookies . . .', 'wait')
        with open(COOKIES_PATH, 'rb') as file:
            cookies = pickle.load(file)
        # print(cookies)
        
        for cookie in cookies:
            driver.add_cookie(cookie)
            # print('Add cookie: ', cookie)
        
        print_banner_colored('Đã add hết toàn bộ cookies', 'success')
        time.sleep(2)
        driver.refresh()
        
        time.sleep(2)
        if not is_login(driver, PATH):
            raise ValueError('Cookie het han roii !!')
    except Exception as e:
        print_banner_colored(f'Thong bao: {e}', 'danger')
        # print_banner_colored('Bắt đầu đăng nhập', 'wait')
        if not is_login(driver, PATH):
            match PATH['NAME']:
                case 'BATDONGSAN':
                    login = Login_Batdongsan(driver)
                case 'CHOTOT':
                    login = Login_Chotot(driver)

            print_banner_colored('Prepare cookies . . .', 'wait')
            login.prepare_cookies()

    print_banner_colored('Đăng nhập thành công', 'success')
    
def is_crawled(link, PATH):
    if PATH['LINK_LIST'].exists():
        link_list = None

        with LOCK_LINK_LIST:
            with open(PATH['LINK_LIST'], 'r') as file:
                try:
                    link_list = json.load(file)
                except:
                    link_list = {}

        return link in link_list

    else:
        return False

def save_link(page_num, link_num, link, PATH):   
    dotenv.load_dotenv()
    with LOCK_LINK_LIST: 
        try:
            with open(PATH['LINK_LIST'], 'r') as file:
                link_list = json.load(file)
        except:
            link_list = {}
                
        link_list[link] = [page_num, link_num, UPDATE_TIME]

        with open(PATH['LINK_LIST'], 'w') as file:
            json.dump(link_list, file)

        update_link_list(PATH)


def save_page_source(page_num, link_num, data, PATH):
    dotenv.load_dotenv()
    folder_storage = os.getenv(PATH['FOLDER_STORAGE_ID_ENV_NAME'])

    # Nếu để name là link thì sẽ fail vì có nhiều kí tự đặc biệt
    file_name = f'u{UPDATE_TIME}_p{page_num}_l{link_num}.json' 
    upload_file(folder_storage, file_name, data_upload=data, type='replace')
    print_banner_colored('Save page source thành công', 'success')


def save_imgs(page_num, link_num, binary_imgs, PATH):
    dotenv.load_dotenv()

    folder_storage_img = os.getenv(PATH['FOLDER_IMG_STORAGE_ID_ENV_NAME'])

    folder_name = f'u{UPDATE_TIME}_p{page_num}_l{link_num}' 
    folder_to_save = create_folder(folder_name, folder_id=folder_storage_img, type='replace')

    folder_to_save_id = folder_to_save['id']

    threads = []
    for index, item in enumerate(binary_imgs):
        file_name = f'u{UPDATE_TIME}_p{page_num}_l{link_num}_{index}.jpg'

        thread = threading.Thread(target=lambda: upload_img(folder_to_save_id, file_name, item, type='replace'))
        threads.append(thread)
        thread.start()
    
    for thread in threads: thread.join()
    
    print_banner_colored('Upload image thành công', 'success')


def save_page_source_need_scraping(page_num, link_num, PATH):
    file_name = f'u{UPDATE_TIME}_p{page_num}_l{link_num}.json'

    try:
        with open(PATH['EXTRACT'], 'r') as file:
            files_need_scraping = json.load(file)
    except:
        files_need_scraping = []
    
    files_need_scraping.append(file_name)

    with open(PATH['EXTRACT'], 'w') as file:
        json.dump(files_need_scraping, file)

    update_extract_info(PATH)
