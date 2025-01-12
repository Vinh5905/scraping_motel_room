from datetime import datetime
import time
import json
import re
import threading
from selenium.webdriver.common.by import By
from shared.support_func import get_new_driver, get_pos_start_crawl, get_link_page, is_login, change_cookies_driver, save_imgs, save_page_source, is_crawled
from shared.colorful import print_banner_colored
from shared.globals import LOCK_DATA, LOCK_PREVIOUS_CRAWL, LOCK_LINK_LIST, CHECKPOINTS_PATH
from msgraph_onedrive.syn import update_crawl_info, update_link_list, update_extract_info

# Wait cho ảnh hiện hết lên rồi mới lấy đượcc

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
        with LOCK_PREVIOUS_CRAWL:
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
        print("START TO GET PAGE")

        page = page or self.__page_num

        if not try_again:
            print_banner_colored(f"LẤY TẤT CẢ LINK CỦA TRANG {page}", 'big')
        # else:
            # self.quit_current_driver()
            # self.driver = get_new_driver(self.__driver_num)

        try: 
            print("GET DRIVER")
            self.driver.get(get_link_page(self.__base_link, page))
            if not is_login(self.driver):
                change_cookies_driver(self.driver)

            all_links = self.get_data_safe('.js__card.js__card-full-web > .js__product-link-for-product-id', multi_value=True, attr='href')

            if not len(all_links): 
                raise ValueError("No links found!!!!")
            else:
                print_banner_colored(title=f'(PAGE {page})', style='success')
                return all_links
            
        except:
            print("ERROR SOMETHING SO RESTART RUNNING")
            if try_again < 5:
                print_banner_colored(title=f'(PAGE {page})', style='danger')

                return self.get_all_links_in_page(try_again=(try_again + 1))
            else:
                raise ValueError("Need to get again, can't get this page!!!!")
            

    def get_data_in_link(self, link, try_again = 0):
        time.sleep(3)

        if not try_again:
            print_banner_colored(f"LẤY DỮ LIỆU CỦA BÀI POST {self.__link_num} CỦA PAGE {self.__page_num}", 'small')
        # else:
            # self.quit_current_driver()
            # self.driver = get_new_driver(self.__driver_num)


        try:
            # Start to get open link
            self.driver.get(link)
            # time.sleep(4)  # Maybe wait for script code (sometime not show immediately) --- or don't need to do that, just re-run again:>
            if not is_login(self.driver):
                change_cookies_driver(self.driver)

            phone_number_button_display = self.driver.find_element(By.CSS_SELECTOR, '.js__ob-agent-info + .js__ob-contact-info > .js__phone')
            phone_number_button_display.click()

            time.sleep(4)

            # Page source
            page_source = self.driver.page_source

            # Image
            imgs = self.get_data_safe('.swiper-slide.js__media-item-container div.re__pr-image-cover', multi_value=True)
            imgs = [img.get_attribute('style') or img.get_attribute('data-bg') for img in imgs]
            for index in range(len(imgs)):
                imgs[index] = re.sub(r'"', r"'", imgs[index])
                imgs[index] = re.sub(r"[\s\S]+(url\('([\s\S]+)'\))[\s\S]*", r"\2", imgs[index])


            # TIME CRAWL THIS POST
                # Need to change datetime type to string before save into json file (if not -> TypeError: Object of type datetime is not JSON serializable)
                # Example of ISO Format: 2021-07-27T16:02:08.070557
            now = {
                'time_scraping': datetime.now().isoformat()
            }

            if not page_source:
                raise ValueError("PAGE SOURCE NO VALUE ???")

            data = {
                'link': link,
                'time_crawling': now,
                'page_source': page_source
            }

            print_banner_colored('Lấy xong dữ liệu từ url', 'success')
            return (data, imgs)

        except:            
            if try_again <= 5:
                print_banner_colored(title=f'(PAGE {self.__page_num}) - (LINK {self.__link_num})', style='danger')

                return self.get_data_in_link(link, try_again=(try_again + 1))
            else:
                raise ValueError("Can't get data from this page for some reason!!;!!")
    
    def save_change_page_link_num(self, page_num, link_num, value_to_stop, exist=False):
        with LOCK_PREVIOUS_CRAWL:
            with open(CHECKPOINTS_PATH['CRAWL'], 'r') as file:
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

        with LOCK_PREVIOUS_CRAWL:
            with open(CHECKPOINTS_PATH['CRAWL'], 'w') as file:
                json.dump(multi_crawl_change, file)

            update_crawl_info()

        if exist:
            print_banner_colored(title=f'(PAGE {page_num}) - (LINK {link_num - 1})', style='exist')
        else:
            print_banner_colored(title=f'(PAGE {page_num}) - (LINK {link_num - 1})', style='success')


    def quit_current_driver(self):
        self.driver.quit()
            
    def crawl(self):
        while True:
            all_links = self.get_all_links_in_page()
            count_link = len(all_links)

            for index in range(self.__link_num, count_link):
                if is_crawled(all_links[index]):
                    self.save_change_page_link_num(self.__page_num, self.__link_num + 1, count_link, exist=True)
                    continue

                data = self.get_data_in_link(all_links[index])

                # Save data
                with LOCK_DATA: 
                    save_page_source(self.__page_num, self.__link_num, data[0])
                save_imgs(self.__page_num, self.__link_num, data[1])
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