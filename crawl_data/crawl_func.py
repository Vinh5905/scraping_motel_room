from pathlib import Path
import random
import time
import re
import json
import pprint
import threading
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from crawl_data.support_func import string_to_dict, print_banner_colored
from global_variable.variable_file_reader import proxies_list
from global_variable.variable_static import lock_data, lock_previous_crawl
from working_with_file.file_func import save_page_source

def get_proxy_random(proxies_list_custom = None): 
    # If not have custom, get global value
    proxies = proxies_list_custom or proxies_list

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
    chrome_service = Service(f'/Users/hoangvinh/OneDrive/Workspace/Support/Driver/chromedriver-mac-x64_{str(driver_num)}/chromedriver')

    if not chorme_options_custom:
        chrome_options.add_argument("--start-maximized")
        # chrome_options.add_argument('--ignore-ssl-errors=yes')
        # chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument("--incognito")
        chrome_options.proxy = get_proxy_random()

        # user_agent_string = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        # chrome_options.add_argument(f"user-agent={user_agent_string}")

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
    path_previous_crawl = Path('./working_with_file/save_data/previous_crawl_info.json')
    previous_crawl = None

    try:
        with open(path_previous_crawl, 'r') as file:
            previous_crawl = json.load(file)
    except:
        with open(path_previous_crawl, 'w') as file:
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

            with open(path_previous_crawl, 'w') as file:
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

    with open(path_previous_crawl, 'w') as file:
        json.dump(new_crawl, file)

    return [new_page_crawling['page'], new_page_crawling['link']]
    
class Crawl:
    __base_link = None
    __page_num = None
    __link_num = None
    __driver_num = None

    def __init__(self, base_link, driver_num = 1):
        self.__base_link = base_link
        self.__driver_num = driver_num
        self.driver = get_new_driver(self.__driver_num)

        # Get pos .....
        with lock_previous_crawl:
            self.__page_num, self.__link_num = get_pos_start_crawl()

    def get_data_safe(self, text_selector, scope_element = None, multi_value = False, return_text = False, attr = ''):
        scope_element = scope_element or self.driver
        try:
            if multi_value:
                elements = scope_element.find_elements(By.CSS_SELECTOR, value = text_selector)

                if len(elements) == 0: return None
                if return_text:
                    return [element.text for element in elements]
                elif attr:
                    return [element.get_attribute(attr) for element in elements if element.get_attribute(attr)]
                else:
                    return elements 
            else:
                element = scope_element.find_element(By.CSS_SELECTOR, value = text_selector)
                if return_text:
                    return element.text
                elif attr:
                    return element.get_attribute(attr)
                else:
                    return elements 
        except:
            return None
        

    def get_all_links_in_page(self, page = None, try_again = 0):
        time.sleep(3)
        page = page or self.__page_num

        if not try_again:
            print_banner_colored(f"LẤY TẤT CẢ LINK CỦA TRANG {page}", 'big')
        else:
            self.quit_current_driver()
            self.driver = get_new_driver(self.__driver_num)

        try: 
            self.driver.get(get_link_page(self.__base_link, page))

            all_links = self.get_data_safe('.js__card.js__card-full-web > .js__product-link-for-product-id', multi_value=True, attr='href')

            if not len(all_links): 
                raise ValueError("No links found!!!!")
            else:
                print_banner_colored(title=f'(PAGE {page})', style='success')
                return all_links
            
        except:
            if try_again < 5:
                print_banner_colored(title=f'(PAGE {page})', style='danger')

                return self.get_all_links_in_page(try_again=(try_again + 1))
            else:
                raise ValueError("Need to get again, can't get this page!!!!")
            

    def get_data_in_link(self, link, try_again = 0):
        time.sleep(3)

        if not try_again:
            print_banner_colored(f"LẤY DỮ LIỆU CỦA BÀI POST {self.__link_num} CỦA PAGE {self.__page_num}", 'small')
        else:
            self.quit_current_driver()
            self.driver = get_new_driver(self.__driver_num)
        try:
            # Start to get open link
            self.driver.get(link)
            # time.sleep(4)  # Maybe wait for script code (sometime not show immediately) --- or don't need to do that, just re-run again:>

            page_source = self.driver.page_source

            if not page_source:
                raise ValueError("PAGE SOURCE NO VALUE ???")

            data = {
                'link': link,
                'page_source': page_source
            }

            return data

        except:            
            if try_again <= 5:
                print_banner_colored(title=f'(PAGE {self.__page_num}) - (LINK {self.__link_num})', style='danger')

                return self.get_data_in_link(link, try_again=(try_again + 1))
            else:
                raise ValueError("Can't get data from this page for some reason!!!!")
    
    def save_change_page_link_num(self, page_num, link_num, value_to_stop):
        path_previous_crawl = Path('./working_with_file/save_data/previous_crawl_info.json')

        with lock_previous_crawl:
            with open(path_previous_crawl, 'r') as file:
                multi_crawl_change = json.load(file)

        for index, item in enumerate(multi_crawl_change['running_thread']):
            if item['page'] == page_num:
                if link_num == value_to_stop:
                    for index_check, item_check in enumerate(multi_crawl_change['running_thread']):
                        if not item_check['isCrawling']:
                            multi_crawl_change['running_thread'][index_check]['isCrawling'] = True
                            self.__page_num = item_check['page']
                            self.__link_num = item_check['link']

                            multi_crawl_change['running_thread'].pop(index)
                            break
                    else:
                        self.__page_num = multi_crawl_change['next_page']
                        self.__link_num = 0

                        multi_crawl_change['next_page'] += 1
                        multi_crawl_change['running_thread'][index]['page'] = self.__page_num
                        multi_crawl_change['running_thread'][index]['link'] = self.__link_num
                else:
                    self.__link_num = link_num

                    multi_crawl_change['running_thread'][index]['link'] = self.__link_num

                break

        with lock_previous_crawl:
            with open(path_previous_crawl, 'w') as file:
                json.dump(multi_crawl_change, file)

        print_banner_colored(title=f'(PAGE {page_num}) - (LINK {link_num - 1})', style='success')


    def quit_current_driver(self):
        self.driver.quit()
            
    def crawl(self):
        while True:
            all_links = self.get_all_links_in_page()
            count_link = len(all_links)

            for index in range(self.__link_num, count_link):
                data = self.get_data_in_link(all_links[index])

                # Save data (data normal and page source)
                with lock_data: 
                    save_page_source(self.__page_num, data)
                    # save_data(data)
                # If success then change file previous_crawl.txt to next post
                self.save_change_page_link_num(self.__page_num, self.__link_num + 1, count_link)

class MultiCrawl:
    def __init__(self, base_link, count_driver): 
        self.__base_link = base_link
        self.__count_driver = count_driver

    def crawl(self):
        for i in range(self.__count_driver):
            single_crawl = Crawl(self.__base_link, i + 1)
            thread = threading.Thread(target=single_crawl.crawl)
            thread.start()