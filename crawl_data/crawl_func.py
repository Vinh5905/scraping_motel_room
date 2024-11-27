from pathlib import Path
import random
import time
import re
import json
import pprint
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from global_variable.variable_file_reader import proxies_list
from crawl_data.support_func import string_to_dict, print_banner_colored
from datetime import datetime
from working_with_file.file_func import save_data
from selenium.webdriver.chrome.service import Service

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
    previous_multi_crawl_path = Path('./working_with_file/save_data/previous_multi_crawl.json')
    previous_crawl = None

    try:
        with open(previous_multi_crawl_path, 'r') as file:
            previous_crawl = json.load(file)
    except:
        with open(previous_multi_crawl_path, 'w') as file:
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

            with open(previous_multi_crawl_path, 'w') as file:
                json.dump(previous_crawl, file)

            print("Start to get: ", previous_crawl)

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

    with open(previous_multi_crawl_path, 'w') as file:
        json.dump(new_crawl, file)

    return [new_page_crawling['page'], new_page_crawling['link']]
    
class Crawl:
    __base_link = None
    __page_num = None
    __link_num = None
    __driver_num = None
    __lock_data = None
    __lock_previous_crawl = None

    def __init__(self, base_link, driver_num, lock_data = None, lock_previous_crawl = None):
        self.__base_link = base_link
        self.__driver_num = driver_num
        self.driver = get_new_driver(self.__driver_num)
        self.__lock_data = lock_data
        self.__lock_previous_crawl = lock_previous_crawl

        # Get pos .....
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
        # DATA IN SCRIPT ELEMENT (NOT SHOW IN UI - ABOUT PRODUCT) - see in ./image/example/undisplayed_data.png
            # Get data inside all script elements
            script_elements = self.get_data_safe('script[type="text/javascript"]', multi_value=True, attr='innerHTML') # script
            undisplayed_data_container = '' # contain text inside script
            for script in script_elements:
                # If conditions is correct then that is element we need (only one exists)
                if script.find('getListingRecommendationParams') != -1:
                    undisplayed_data_container = script
                    break

            # Position of the dict we need in type string (start - end)
            undisplayed_text_start = 0
            undisplayed_text_end = 0

            # You can see picture to know why
            for i in range(len(undisplayed_data_container)):
                # get nearest {
                if undisplayed_data_container[i] == '{': 
                    undisplayed_text_start = i
                # get first }
                if undisplayed_data_container[i] == '}':
                    undisplayed_text_end = i
                    break
            
            # Get dict but in type string
            undisplayed_in_curly_braces = undisplayed_data_container[undisplayed_text_start:(undisplayed_text_end + 1)]
            # Change to dict
            undisplayed_info = string_to_dict(undisplayed_in_curly_braces)
            # print(undisplayed_info)


        # DATA IN SCRIPT ELEMEMENT (CAN SHOW SOME IN UI - ABOUT LANDLORD) - see in ./image/example/landlord.png
            landlord_data_container = ''
            for script in script_elements:
                if script.find('FrontEnd_Product_Details_ContactBox') != -1:
                    landlord_data_container = script
                    break
            
            # Set start from {  (see image to understand why)
            landlord_text_start = landlord_data_container.index('window.FrontEnd_Product_Details_ContactBox')
            landlord_text_start = landlord_data_container.find('{', landlord_text_start)
            landlord_text_end = 0

            landlord_container_from_first_curly_braces = landlord_data_container[landlord_text_start:]


            # Try to find } close dict, use stack to find
            array = [] # contain { } , as same as stack
            for i in range(len(landlord_container_from_first_curly_braces)):
                if landlord_container_from_first_curly_braces[i] == '{': 
                    array.append(landlord_container_from_first_curly_braces[i])
                if landlord_container_from_first_curly_braces[i] == '}':
                    array.pop()
                    if len(array) == 0:
                        landlord_text_end = i + 1
                        break

            landlord_in_curly_braces = landlord_container_from_first_curly_braces[0:landlord_text_end] 

            # Error parseInt when change to dict, so erase it - see image to know where is it
            landlord_in_curly_braces = re.sub(r'(parseInt\(("(\d+)")\))', r'\3', landlord_in_curly_braces)  

            # Change to dict
            landlord_info = string_to_dict(landlord_in_curly_braces)

            # Get many key, but only some can be used
            key_needed = ['nameSeller', 'emailSeller', 'userId']
            landlord_needed_info = {key: value for key, value in landlord_info.items() if key in key_needed}
            # print(landlord_needed_info)

        # DATA SHOW IN UI (everything you see when open website - ABOUT PRODUCT)
            displayed_data_container = {}

            # Link of post
            displayed_data_container['Link'] = link
            # Title of post
            displayed_data_container['Title'] = self.get_data_safe('.re__pr-title.pr-title.js__pr-title', return_text=True)
            # Address
            displayed_data_container['Address'] = self.get_data_safe('.re__pr-short-description.js__pr-address', return_text=True)
            # Vertified from batdongsan
            displayed_data_container['Verified'] = self.get_data_safe('.re__pr-stick-listing-verified') or None
            # Image links - string
            img_links = self.get_data_safe('.re__media-thumb-item.js__media-thumbs-item > img', multi_value=True, attr='src')
            displayed_data_container['Images'] = ','.join(img_links)

            # Example in ./image/example/a.png
            a = self.get_data_safe('.re__pr-short-info-item.js__pr-short-info-item', multi_value=True)
            for couple in a:
                key = self.get_data_safe('.title', scope_element=couple, return_text=True)
                if not key: continue # if not exists then passs

                value = self.get_data_safe('.value', scope_element=couple, return_text=True)
                # Some post have ext info below
                ext = self.get_data_safe('.ext', scope_element=couple, return_text=True)
                
                displayed_data_container[key] = value
                displayed_data_container[key + ' ' + 'ext'] = ext

            displayed_data_container['Detail'] = self.get_data_safe('.re__detail-content', return_text=True)

            # Example in ./image/example/b.png
            b = self.get_data_safe('.re__pr-specs-content-item', multi_value=True)
            for couple in b:
                key = self.get_data_safe('.re__pr-specs-content-item-title', scope_element=couple, return_text=True)
                if not key: continue # if not exists then passs

                value = self.get_data_safe('.re__pr-specs-content-item-value', scope_element=couple, return_text=True)

                displayed_data_container[key] = value        

            # Example in ./image/example/c.png
            c = self.get_data_safe('.re__pr-short-info-item.js__pr-config-item', multi_value=True)
            for couple in c:
                key = self.get_data_safe('.title', scope_element=couple, return_text=True)
                if not key: continue # if not exists then passs

                value = self.get_data_safe('.value', scope_element=couple, return_text=True)

                displayed_data_container[key] = value    
            # print(displayed_data_container)

        # TIME CRAWL THIS POST
            # Need to change datetime type to string before save into json file (if not -> TypeError: Object of type datetime is not JSON serializable)
            # Example of ISO Format: 2021-07-27T16:02:08.070557
            now = {
                'time_scraping': datetime.now().isoformat()
            }

            # print(now)

            full_data = {}
            full_data.update(undisplayed_info)
            full_data.update(landlord_needed_info)
            full_data.update(displayed_data_container)
            full_data.update(now)

            data = {
                'data': full_data,
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
        previous_multi_crawl_path = Path('./working_with_file/save_data/previous_multi_crawl.json')

        with open(previous_multi_crawl_path, 'r') as file:
            multi_crawl_change = json.load(file)
        print("CURRENT : ", multi_crawl_change)

        for index, item in enumerate(multi_crawl_change['running_thread']):
            if item['page'] == page_num:
                if link_num == value_to_stop:
                    self.__page_num = multi_crawl_change['next_page']
                    self.__link_num = 0

                    multi_crawl_change['next_page'] += 1
                    multi_crawl_change['running_thread'][index]['page'] = self.__page_num
                    multi_crawl_change['running_thread'][index]['link'] = self.__link_num
                else:
                    self.__link_num = link_num

                    multi_crawl_change['running_thread'][index]['link'] = self.__link_num

                break

        print("NEXT POST INFO : ", multi_crawl_change)
        with open(previous_multi_crawl_path, 'w') as file:
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
                save_data(data)
                print("CURRENT INDEX OF LINK WHEN CRAWL: ", index)
                # If success then change file previous_crawl.txt to next post
                self.save_change_page_link_num(self.__page_num, self.__link_num + 1, count_link)

class MultiCrawl:
    def __init__(self, base_link, count_driver): 
        self.__base_link = base_link
        self.__count_driver = count_driver
        self.__lock_data = threading.Lock()
        self.__lock_previous_crawl = threading.Lock()

    def crawl(self):
        for i in range(self.__count_driver):
            single_crawl = Crawl(self.__base_link, i + 1)
            thread = threading.Thread(target=single_crawl.crawl)
            thread.start()
