import json
import pprint
import re
import sys
import time
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

from crawl_data.support_func import string_to_dict
from crawl_data.crawl_func import get_new_driver
from crawl_data.support_func import print_banner_colored

def get_data_in_link(link, try_again = 0):
    time.sleep(3)

    if not try_again:
        print_banner_colored(f"LẤY LẠI DỮ LIỆU CỦA BÀI POST", 'small')
    else:
        driver = get_new_driver()

    try:
        # Start to get open link
        driver.get(link)
        # time.sleep(20)  # Maybe wait for script code (sometime not show immediately) --- or don't need to do that, just re-run again:>

        page_source = driver.page_source

        if not page_source:
            raise ValueError("PAGE SOURCE NO VALUE ???")

        return page_source

    except:            
        if try_again < 5:
            print_banner_colored(title=f'GET PAGE SOURCE AGAIN LINK....', style='danger')

            return get_data_in_link(link, try_again=(try_again + 1))
        else:
            sys.exit("KHẢ NĂNG BỊ MẤT MẠNG")

class Extract():
    def __init__(self):
        path_previous_crawl = Path('./working_with_file/save_data/previous_crawl_info.json')
        path_previous_extract = Path('./working_with_file/save_data/previous_extract_info.json')

        # Get max page can extract
        with open(path_previous_crawl, 'r') as file:
            try:
                info_crawl = json.load(file)
            except:
                raise ValueError("STILL NOT HAVE ANY PAGE CRAWL DONE !!")

            self.page_to_stop = float('inf')
            for item in info_crawl['running_thread']:
                self.page_to_stop = min(self.page_to_stop, item['page'] - 1)

            if self.page_to_stop == 0:
                raise ValueError("STILL NOT HAVE ANY PAGE CRAWL DONE !!")
        
        with open(path_previous_extract, 'r') as file:
            self.page_start = json.load(file)


    def get_data_safe(self, soup, text_selector, multi_value = False, return_text = False, attr = ''):
        try:
            if multi_value:
                elements = soup.select(text_selector)

                if len(elements) == 0: return None
                if return_text:
                    return [element.get_text() for element in elements]
                elif attr:
                    return [element[attr] for element in elements if element[attr]]
                else:
                    return elements 
            else:
                element = soup.select_one(text_selector)
                if return_text:
                    return element.get_text()
                elif attr:
                    return element[attr]
                else:
                    return element 
        except:
            return None
        

    def extract_one_page_source(self, link, page_source, index):
        page_source_data = page_source

        try:
            if page_source_data == '':
                raise ValueError()
        
            soup = BeautifulSoup(page_source_data, 'html.parser')

        # DATA SHOW IN UI (everything you see when open website - ABOUT PRODUCT)
            displayed_data_container = {}
            # Link post
            displayed_data_container['Link'] = link
            # Title of post
            displayed_data_container['Title'] = self.get_data_safe(soup, '.re__pr-title.pr-title.js__pr-title', return_text=True)
            # Address
            displayed_data_container['Address'] = self.get_data_safe(soup, '.re__pr-short-description.js__pr-address', return_text=True)
            # Vertified from batdongsan
            displayed_data_container['Verified'] = self.get_data_safe(soup, '.re__pr-stick-listing-verified') is not None
            # Image links - string
            img_links = self.get_data_safe(soup, '.re__media-thumb-item.js__media-thumbs-item > img', multi_value=True, attr='src')
            if img_links:
                displayed_data_container['Images'] = ','.join(img_links)
            else:
                displayed_data_container['Images'] = None

            # Example in ./image/example/a.png
            a = self.get_data_safe(soup, '.re__pr-short-info-item.js__pr-short-info-item', multi_value=True)
            for couple in a:
                key = self.get_data_safe(couple, '.title', return_text=True)
                if not key: continue # if not exists then passs

                value = self.get_data_safe(couple, '.value', return_text=True)
                # Some post have ext info below
                ext = self.get_data_safe(couple, '.ext', return_text=True)
                
                displayed_data_container[key] = value
                displayed_data_container[key + ' ' + 'ext'] = ext

            # Example in ./image/example/b.png
            b = self.get_data_safe(soup, '.re__pr-specs-content-item', multi_value=True)
            for couple in b:
                key = self.get_data_safe(couple, '.re__pr-specs-content-item-title', return_text=True)
                if not key: continue # if not exists then passs

                value = self.get_data_safe(couple, '.re__pr-specs-content-item-value', return_text=True)

                displayed_data_container[key] = value   

            # Example in ./image/example/c.png
            c = self.get_data_safe(soup, '.re__pr-short-info-item.js__pr-config-item', multi_value=True)
            for couple in c:
                key = self.get_data_safe(couple, '.title', return_text=True)
                if not key: continue # if not exists then passs

                value = self.get_data_safe(couple, '.value', return_text=True)

                displayed_data_container[key] = value  

            # pprint.pprint(displayed_data_container)

        # DATA IN SCRIPT ELEMENT (NOT SHOW IN UI - ABOUT PRODUCT) - see in ./image/example/undisplayed_data.png
            # Get data inside all script elements
            script_elements = self.get_data_safe(soup, 'script[type="text/javascript"]', multi_value=True, return_text=True) # script
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

            # pprint.pprint(undisplayed_info)

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

            # pprint.pprint(landlord_info)

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

            print_banner_colored(f'Link {index} success', 'success')
            return full_data
        except KeyboardInterrupt:
            sys.exit("NGẮT CHƯƠNG TRÌNH TỪ BÀN PHÍM !!")
        except:
            print_banner_colored(f'Link {index} failed', 'danger')
            return None
    
    
    def extract(self):
        for page in range(self.page_start, self.page_to_stop + 1):
            print_banner_colored(f'Extract data in page {page}', 'small')
            path_to_page_source = Path(f'./working_with_file/save_data/data/page_{page}/page_source.json')
            path_to_data = Path(f'./working_with_file/save_data/data/page_{page}/data.json')
            path_previous_extract = Path('./working_with_file/save_data/previous_extract_info.json')

            with open(path_to_page_source, 'r') as file:
                all_page_source = json.load(file)
            
            all_data_extracted = []

            for index, (link, page_source) in enumerate(all_page_source.items()):
                data_extracted = self.extract_one_page_source(link, page_source, index)

                if not data_extracted:
                    try_again = 0
                    while (not data_extracted) and (try_again < 5):
                        alter_page_source = get_data_in_link(link)
                        data_extracted = self.extract_one_page_source(link, alter_page_source, index)
                        try_again += 1
                    
                    if data_extracted:
                        all_page_source[link] = alter_page_source
                        with open(path_to_page_source, 'w') as file:
                            json.dump(all_page_source, file)
                    
                if data_extracted:
                    all_data_extracted.append(data_extracted)

            with open(path_to_data, 'w') as file:
                json.dump(all_data_extracted, file, ensure_ascii=False)

            with open(path_previous_extract, 'w') as file:
                json.dump(page + 1, file, ensure_ascii=False)

if __name__ == '__main__':
    run = Extract()
    run.extract()

    