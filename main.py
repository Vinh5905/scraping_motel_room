from crawl_data.crawl_func import crawl

# Cần chỉnh sửa cho từng error như timeout, privacy, ...

if __name__ == '__main__':
    base = 'https://batdongsan.com.vn/cho-thue-nha-tro-phong-tro-tp-hcm'

    crawl(base)