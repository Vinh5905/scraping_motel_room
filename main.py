from crawl.crawl import MultiCrawl
from scraping.scraping_func import Extract
from shared.support_func import return_PATH

if __name__ == '__main__':  

    print('Bạn muốn vào thực hiện hành động với web nào ?')
    print('[B] Batdongsan           [C] Chotot')
    web_input = input('Answer: ')
    match web_input:
        case 'B' | 'b':
            web = 'BATDONGSAN'
        case 'C' | 'c':
            web = 'CHOTOT'
        case '_':
            raise ValueError('WRONG INPUT !!!')


    print(f'Bạn muốn vào chế độ TEST hay REAL của {web}?')
    print('[T] TEST           [R] REAL')
    test_input = input('Answer: ')
    match test_input:
        case 'T' | 't':
            test = True
        case 'R' | 'r':
            test = False
        case '_':
            raise ValueError('WRONG INPUT !!!')

    # PATH
    PATH = return_PATH(web, test)

    print('Bạn muốn Crawling hay Scraping?')
    print('[C] Crawling           [S] Scraping')
    action_input = input('Answer: ')
    match action_input:
        case 'C' | 'c':
            run = MultiCrawl(PATH)
            run.crawl()    
        case 'S' | 's':
            run = Extract(PATH)
            run.extract()
        case '_':
            raise ValueError('WRONG INPUT !!!')
