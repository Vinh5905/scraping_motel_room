import ast
import random
import re
import json
import pickle
import os
from pathlib import Path
import time
# from bs4 import BeautifulSoup
# from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from shared.globals import TERMINAL_WIDTH, PROXIES_LIST, SAVE_DATA_PATH, CHECKPOINTS_PATH, COOKIES_PATH, DRIVER_PATH, LOCK_LINK_LIST
from login.login import Login
from msgraph_onedrive.operations import upload_file
import dotenv
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

def reset_previous_crawl():
    try:
        with open(CHECKPOINTS_PATH['CRAWL'], 'r') as file:
            previous_multi_crawl = json.load(file)

        for index in range(len(previous_multi_crawl['running_thread'])):
            previous_multi_crawl['running_thread'][index]['isCrawling'] = False

        with open(CHECKPOINTS_PATH['CRAWL'], 'w') as file:
            json.dump(previous_multi_crawl, file)
    except:
        return        

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


def get_new_driver(driver_num = 1, chorme_options_custom = None):
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
        # chrome_options.add_argument("--start-maximized")
        # chrome_options.add_argument('--ignore-ssl-errors=yes')
        # chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument("--incognito")
        # chrome_options.proxy = get_proxy_random()

    driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    # driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.implicitly_wait(5)

    return driver


def get_link_page(base_link, page_num):
    if page_num == 1: 
        # Keep origin because page 1 is as same as base link
        return base_link
    else: 
        return f'{base_link}/p{page_num}'


def get_pos_start_crawl():
    previous_crawl = None

    try:
        with open(CHECKPOINTS_PATH['CRAWL'], 'r') as file:
            previous_crawl = json.load(file)
    except:
        with open(CHECKPOINTS_PATH['CRAWL'], 'w') as file:
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

            with open(CHECKPOINTS_PATH['CRAWL'], 'w') as file:
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

    with open(CHECKPOINTS_PATH['CRAWL'], 'w') as file:
        json.dump(new_crawl, file)

    return [new_page_crawling['page'], new_page_crawling['link']]


def is_login(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, '#kct_login')
        print_banner_colored('Đã login', 'success')
        return False
    except:
        # print_banner_colored('Chưa login', 'wait')
        return True

def change_cookies_driver(driver):
    # print_banner_colored('Bắt đầu đăng nhập', 'wait')
    if not is_login(driver):
        print("CHUA LOGIN NEN BAT DAU PREPARE COOKIES")
        login = Login(driver)
        login.prepare_cookies()
    print_banner_colored('Đăng nhập thành công', 'success')
    
def is_crawled(link):
    if CHECKPOINTS_PATH['LINK_LIST'].exists():
        link_list = None

        with LOCK_LINK_LIST:
            with open(CHECKPOINTS_PATH['LINK_LIST'], 'r') as file:
                try:
                    link_list = json.load(file)
                except:
                    link_list = {}

        return link in link_list

    else:
        return False

def save_link(page_num, link_num, update_num, link):   
    dotenv.load_dotenv()
    with LOCK_LINK_LIST: 
        try:
            with open(CHECKPOINTS_PATH['LINK_LIST'], 'r') as file:
                link_list = json.load(file)
        except:
            link_list = {}
                
        link_list[link] = [page_num, link_num, update_num]

        with open(CHECKPOINTS_PATH['LINK_LIST'], 'w') as file:
            json.dump(link_list, file)

        update_link_list()


def save_page_source(page_num, link_num, data):
    update_num = 0
    dotenv.load_dotenv()

    # Nếu để name là link thì sẽ fail vì có nhiều kí tự đặc biệt
    filename = f'p{page_num}_l{link_num}_u{update_num}.json' 
    upload_file(os.getenv('FOLDER_STORAGE_ID'), filename, data_upload=data, type='replace')
    print_banner_colored('Save page source thành công', 'success')

    save_link(page_num, link_num, update_num, data['link'])

def save_imgs(page_num, link_num, img_links):
    # -> Tạo folder riêng
    # -> Add từng ảnh vào folder