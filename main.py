from crawl_data.crawl_func import Crawl
import time

# Cần chỉnh sửa cho từng error như timeout, privacy, ...

if __name__ == '__main__':
    base = 'http://batdongsan.com.vn/cho-thue-nha-tro-phong-tro-tp-hcm'
    
    run = Crawl(base, 1)
    run.crawl()