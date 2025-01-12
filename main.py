from crawl.crawl import MultiCrawl, Crawl
from shared.support_func import reset_previous_crawl

'''
- Multiple:
    + Tạo cấu trúc file để change sau mỗi lần crawl để trách bị đè lên nhau 
        Cấu trúc :
            {   
                next_page: ...,
                running_thread: [
                    {
                        page,
                        link,
                        isCrawl
                    }
                ]
            }
    + Dùng thread để chạy nhiều crawl() liên tiếp, dùng lock cho save, thay đổi giá trị của file trên.

    + Lưu ý từng bước :
        * Reset lại trạng thái thành False hết cho lần chạy mới

        * Khi lần đầu vô, check các lần crawl trước đó : (lock)
            - Nếu đã xuất hiện thì check từ trên xuống, isCrawl False thì lấy đó là đổi thành True
            - Nếu tất cả đều True hoặc chưa có gì, thì lấy page của next_page để tạo và add vào running_thread, và sau đó next_page + 1

        * Lúc save file (lock)

        * Sau khi chạy xong hết đến 20 rồi thì tiếp tục từ next_page
        
        * Chạy xong mà bị end chương trình là isCrawl thành False hết.
'''

if __name__ == '__main__':  
    base = 'http://batdongsan.com.vn/cho-thue-nha-tro-phong-tro-tp-hcm'
    reset_previous_crawl()

    run = MultiCrawl(base, 1)
    run.crawl()

    # run = Crawl(base)
    # run.crawl()
    # run.get_data_in_link('https://batdongsan.com.vn/cho-thue-nha-tro-phong-tro-duong-pham-huu-lau-xa-phuoc-kieng/-2tr9-day-du-tien-nghi-noi-that-wc-chung-co-n-vien-ve-sinh-bep-camera-24-24-pr41376284')
    