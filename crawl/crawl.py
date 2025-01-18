from datetime import datetime
import time
import json
import re
import threading
from selenium.webdriver.common.by import By
from shared.support_func import get_new_driver, get_pos_start_crawl, get_link_page, is_login, change_cookies_driver, save_imgs, save_page_source, is_crawled, base64_to_binary, save_link, reset_previous_crawl, save_page_source_need_scraping
from shared.colorful import print_banner_colored
from shared.globals import LOCK_DATA, LOCK_PREVIOUS_CRAWL, LOCK_LINK_LIST, CHECKPOINTS_PATH, CHECKPOINTS_PATH_TEST, COOKIES_PATH
from msgraph_onedrive.syn import update_crawl_info, update_link_list, update_extract_info, pull_from_onedrive

# Wait cho ảnh hiện hết lên rồi mới lấy đượcc

class Crawl:
    __base_link = None
    __page_num = None
    __link_num = None
    __driver_num = None
    __security = False

    def __init__(self, PATH, driver_num = 1):
        self.PATH = PATH
        self.__driver_num = driver_num

        match (self.PATH['NAME']):
            case 'BATDONGSAN':
                self.__base_link = 'http://batdongsan.com.vn/cho-thue-nha-tro-phong-tro-tp-hcm'
            case 'CHOTOT':
                self.__security = True
                self.__base_link = 'https://www.nhatot.com/thue-phong-tro-tp-ho-chi-minh'

        self.driver = get_new_driver(driver_num=self.__driver_num, security=self.__security)
        
        # Get pos .....
        with LOCK_PREVIOUS_CRAWL:
            self.__page_num, self.__link_num = get_pos_start_crawl(self.PATH)

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

    def get_base64_imgs(self, img_links):
        self.driver.execute_script('''
            window.getBase64FromImageUrl = async function(url) {
                return new Promise((resolve, reject) => {
                    var img = new Image();
                    img.crossOrigin = 'anonymous'; // CORS bypass
                    img.onload = function () {
                        var canvas = document.createElement("canvas");
                        canvas.width = this.width;
                        canvas.height = this.height;

                        var ctx = canvas.getContext("2d");
                        ctx.drawImage(this, 0, 0);

                        var dataURL = canvas.toDataURL("image/jpeg"); // Export Base64 as JPEG
                        resolve(dataURL);
                    };

                    img.onerror = function () {
                        reject("Failed to load image from URL.");
                    };

                    img.src = url;
                });
            };
        ''')   

        imgs_base64 = []

        for i in range(len(img_links)):
            base64_data = self.driver.execute_script(f'return getBase64FromImageUrl("{img_links[i]}")')
            imgs_base64.append(base64_data)

        return imgs_base64
    

    def get_all_links_in_page(self, page = None, try_again = 0):
        time.sleep(3)

        page = page or self.__page_num

        if not try_again:
            print_banner_colored(f"LẤY TẤT CẢ LINK CỦA TRANG {page}", 'big')
        # else:
            # self.quit_current_driver()
            # self.driver = get_new_driver(self.__driver_num)

        try: 
            self.driver.get(get_link_page(self.__base_link, page, self.PATH))
            if not is_login(self.driver, self.PATH):
                change_cookies_driver(self.driver, self.PATH)

            match self.PATH['NAME']:
                case 'BATDONGSAN':
                    all_links = self.get_data_safe('.js__card.js__card-full-web > .js__product-link-for-product-id', multi_value=True, attr='href')
                case 'CHOTOT':
                    pass

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
        # else:
            # self.quit_current_driver()
            # self.driver = get_new_driver(self.__driver_num)

        try:
            match self.PATH['NAME']:
                case 'BATDONGSAN':
                    # Start to get open link
                    self.driver.get(link)

                    time.sleep(4)  # Maybe wait for script code (sometime not show immediately) --- or don't need to do that, just re-run again:>
                    if not is_login(self.driver, self.PATH):
                        change_cookies_driver(self.driver, self.PATH)

                    phone_number_button_display = self.driver.find_element(By.CSS_SELECTOR, '.js__ob-agent-info + .js__ob-contact-info > .js__phone')
                    phone_number_button_display.click()
                    time.sleep(4)

                    click_again = 0
                    while phone_number_button_display.text.find('***') != -1:
                        phone_number_button_display.click()
                        time.sleep(4)
                        click_again += 1
                        if click_again == 3:
                            raise ValueError('Click khong thanh cong')
                        

                    # Page source
                    page_source = self.driver.page_source

                    # Image
                    imgs = self.get_data_safe('.swiper-slide.js__media-item-container div.re__pr-image-cover', multi_value=True)
                    imgs = [img.get_attribute('style') or img.get_attribute('data-bg') for img in imgs]
                    for index in range(len(imgs)):
                        imgs[index] = re.sub(r'"', r"'", imgs[index])
                        imgs[index] = re.sub(r"[\s\S]+(url\('([\s\S]+)'\))[\s\S]*", r"\2", imgs[index])
                    
                    imgs_base64 = self.get_base64_imgs(imgs)
                    binary_imgs = base64_to_binary(imgs_base64)

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
                    return (data, binary_imgs)
                case 'CHOTOT':
                    pass
                case '_':
                    raise ValueError('KHONG PHU HOP PATH["NAME"]')

        except Exception as e:            
            if try_again <= 5:
                print_banner_colored(title=f'(PAGE {self.__page_num}) - (LINK {self.__link_num})', style='danger')
                print(f'ERROR: {e}')

                return self.get_data_in_link(link, try_again=(try_again + 1))
            else:
                check = input('VẤN ĐỀ CÓ THỂ DO NETWORK HOẶC POP UP KHÔNG XÁC ĐỊNH, CRAWL LẠI?  [Y] Yes   [N] No      : ')
                match check:
                    case 'Y' | 'y':
                        crawl = MultiCrawl(self.PATH)
                        crawl.crawl()
                    case '_':
                        raise ValueError("Can't get data from this page for some reason!!;!!")
    
    def save_change_page_link_num(self, page_num, link_num, value_to_stop, exist=False):
        with LOCK_PREVIOUS_CRAWL:
            with open(self.PATH['CRAWL'], 'r') as file:
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
            with open(self.PATH['CRAWL'], 'w') as file:
                json.dump(multi_crawl_change, file)

            update_crawl_info(self.PATH)

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
                if is_crawled(all_links[index], self.PATH):
                    self.save_change_page_link_num(self.__page_num, self.__link_num + 1, count_link, exist=True)
                    continue

                data = self.get_data_in_link(all_links[index])

                # Save data
                with LOCK_DATA: 
                    save_page_source(self.__page_num, self.__link_num, data[0], self.PATH)
                    save_page_source_need_scraping(self.__page_num, self.__link_num, self.PATH)

                save_imgs(self.__page_num, self.__link_num, data[1], self.PATH)
                # If success then change file previous_crawl.txt to next post
                save_link(self.__page_num, self.__link_num, data[0]['link'], self.PATH)
                self.save_change_page_link_num(self.__page_num, self.__link_num + 1, count_link)


class MultiCrawl:
    def __init__(self, PATH, count_driver = 1): 
        self.PATH = PATH
        self.__count_driver = count_driver

        PATH['CHECKPOINT'].mkdir(exist_ok=True)
        
        # Nhớ phải để pull trước reset (pull thì isCrawling vẫn là True)
        pull_from_onedrive(PATH)
        reset_previous_crawl(PATH)

    def crawl(self):
        for i in range(self.__count_driver):
            single_crawl = Crawl(self.PATH, driver_num = i + 1)
            thread = threading.Thread(target=single_crawl.crawl)
            thread.start()