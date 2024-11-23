import random
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from global_variable.variable_file_reader import proxies_list
from crawl_data.support_func import string_to_dict, print_banner_colored
from datetime import datetime

def get_proxy_random(proxies_list_custom = None): 
    # If not have custom, get global value
    proxies = proxies_list_custom or proxies_list

    proxy_stt = random.randrange(0, len(proxies))

    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': proxies[proxy_stt],
        'sslProxy': proxies[proxy_stt]
    })

    return proxy

def get_new_driver(chorme_options_custom = None):
    # If not have custom then use default self-config
    chrome_options = chorme_options_custom or webdriver.ChromeOptions()
    # chrome_service = Service(executable_path='./chromedriver-mac-x64/chromedriver')

    if not chorme_options_custom:
        chrome_options.add_argument("--start-maximized")
        # chrome_options.add_argument('--ignore-ssl-errors=yes')
        # chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument("--incognito")
        chrome_options.proxy = get_proxy_random()

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)

    return driver

def get_link_page(base_link, page_num):
    if page_num == 1: 
        # Keep origin because page 1 is as same as base link
        return base_link
    else: 
        return f'{base_link}/p{page_num}'


def get_data_safe(scope_element, text_selector, multi_value = False, return_text = False, attr = ''):
    # Default is driver
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


def get_all_links_in_page(base_link, page_num, try_again = 0):
    time.sleep(2)
    if not try_again:
        print_banner_colored(f"LẤY TẤT CẢ LINK CỦA TRANG {page_num}", 'big')

    try: 
        driver = get_new_driver()
        driver.get(get_link_page(base_link, page_num))

        all_links = get_data_safe(driver, '.js__card.js__card-full-web > .js__product-link-for-product-id', multi_value=True, attr='href')

        if not len(all_links): 
            raise ValueError("No links found!!!!")
        else:
            print_banner_colored(style='success')
            return all_links
    except:
        driver.close()

        if try_again <= 5:
            print_banner_colored(style='try_again')
            return get_all_links_in_page(base_link, page_num, try_again + 1)
        else:
            raise ValueError("Need to get again, can't get this page!!!!")
        

def get_data_in_link(scope_element, link, pos = None, try_again = 0):
    time.sleep(2)

    if not try_again:
        if pos:
            print_banner_colored(f"LẤY DỮ LIỆU CỦA BÀI POST {pos}", 'small')
        else:
            print_banner_colored("LẤY DỮ LIỆU CỦA BÀI POST", 'small')

    try:
        # Start to get open link
        scope_element.get(link)
        time.sleep(4)  # Maybe wait for script code (sometime not show immediately) --- or don't need to do that, just re-run again:>

        page_source = scope_element.page_source
    # DATA IN SCRIPT ELEMENT (NOT SHOW IN UI - ABOUT PRODUCT) - see in ./image/example/undisplayed_data.png
        # Get data inside all script elements
        script_elements = get_data_safe(scope_element, 'script[type="text/javascript"]', multi_value=True, attr='innerHTML') # script
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

    # DATA SHOW IN UI (everything you see when open website - ABOUT PRODUCT)
        displayed_data_container = {}

        # Link of post
        displayed_data_container['Link'] = link
        # Title of post
        displayed_data_container['Title'] = get_data_safe(scope_element, '.re__pr-title.pr-title.js__pr-title', return_text=True)
        # Address
        displayed_data_container['Address'] = get_data_safe(scope_element, '.re__pr-short-description.js__pr-address', return_text=True)
        # Vertified from batdongsan
        displayed_data_container['Verified'] = get_data_safe(scope_element, '.re__pr-stick-listing-verified') or None
        # Image links - string
        img_links = get_data_safe(scope_element, '.re__media-thumb-item.js__media-thumbs-item > img', multi_value=True, attr='src')
        displayed_data_container['Images'] = ','.join(img_links)

        # Example in ./image/example/a.png
        a = get_data_safe(scope_element, '.re__pr-short-info-item.js__pr-short-info-item', multi_value=True)
        for couple in a:
            key = get_data_safe(couple, '.title', return_text=True)
            if not key: continue # if not exists then passs

            value = get_data_safe(couple, '.value', return_text=True)
            # Some post have ext info below
            ext = get_data_safe(couple, '.ext', return_text=True)
            
            displayed_data_container[key] = value
            displayed_data_container[key + ' ' + 'ext'] = ext

        displayed_data_container['Detail'] = get_data_safe(scope_element, '.re__detail-content', return_text=True)

        # Example in ./image/example/b.png
        b = get_data_safe(scope_element, '.re__pr-specs-content-item', multi_value=True)
        for couple in b:
            key = get_data_safe(couple, '.re__pr-specs-content-item-title', return_text=True)
            if not key: continue # if not exists then passs

            value = get_data_safe(couple, '.re__pr-specs-content-item-value', return_text=True)

            displayed_data_container[key] = value        

        # Example in ./image/example/c.png
        c = get_data_safe(scope_element, '.re__pr-short-info-item.js__pr-config-item', multi_value=True)
        for couple in c:
            key = get_data_safe(couple, '.title', return_text=True)
            if not key: continue # if not exists then passs

            value = get_data_safe(couple, '.value', return_text=True)

            displayed_data_container[key] = value    

    # TIME CRAWL THIS POST
        now = {
            'time_scraping': datetime.now()
        }

        full_data = {}
        full_data.update(undisplayed_info)
        full_data.update(landlord_needed_info)
        full_data.update(displayed_data_container)
        full_data.update(now)

        return {
            'data': full_data,
            'page_source': page_source
        }

    except:
        scope_element.close()
        
        if try_again <= 5:
            print_banner_colored(style='try_again')
            return get_data_in_link(get_new_driver(), link, try_again + 1)
        else:
            raise ValueError("Can't get data from this page for some reason!!!!")
        
def crawl(base_link):
    while True:
        with open('./working_with_file/save_data/previous_crawl.txt', 'r') as file:
            page_num, link_num = map(int, file.read().splitlines())

        all_links = get_all_links_in_page(base_link, page_num)
        
        driver = get_new_driver()

        for index, link in enumerate(all_links):
            if index >= link_num: 
                data = get_data_in_link(driver, link, index + 1)
                # print(data['data'])
                # Add to file .... (both data and page_source)
                
                # If success then change file previous_crawl.txt
                with open('./working_with_file/save_data/previous_crawl.txt', 'w') as file:
                    file.write(f'{page_num}\n{index + 1}')
                print_banner_colored(style='success')
        
        with open('./working_with_file/save_data/previous_crawl.txt', 'w') as file:
            file.write(f'{page_num}\n{0}')