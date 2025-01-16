import os
import threading
from pathlib import Path

# PROXIES
PROXIES_RAW_PATH = Path('./proxies/proxies_raw.txt')
PROXIES_VALID_PATH = Path('./proxies/proxies_valid.txt')

# Get proxies list
with open(PROXIES_RAW_PATH, 'r') as file:
    # Use splitlines() to split by lines without \n
    PROXIES_LIST = file.read().splitlines()


# Get terminal size -> print more beautiful :>
TERMINAL_WIDTH = os.get_terminal_size().columns


# LOCK
LOCK_DATA = threading.Lock()
LOCK_PREVIOUS_CRAWL = threading.Lock()
LOCK_LINK_LIST = threading.Lock()


# PATH
ALL_EXTRACTED_DATA_PATH = Path('./data/all_extracted_data/data.csv')

ACCESS_TOKEN = Path('./data/access_token/access_token.json')

CHECKPOINTS_PATH = {
    'BATDONGSAN': {
        'NAME': 'BATDONGSAN',
        'CRAWL': Path('./data/checkpoints_batdongsan/previous_crawl_info.json'),
        'EXTRACT': Path('./data/checkpoints_batdongsan/previous_extract_info.json'),
        'LINK_LIST': Path('./data/checkpoints_batdongsan/previous_link_list.json')
    },
    'CHOTOT': {
        'NAME': 'CHOTOT',
        'CRAWL': Path('./data/checkpoints_chotot/previous_crawl_info.json'),
        'EXTRACT': Path('./data/checkpoints_chotot/previous_extract_info.json'),
        'LINK_LIST': Path('./data/checkpoints_chotot/previous_link_list.json')
    }
}

COOKIES_PATH = Path('./data/cookies/cookies.pkl')

SAVE_DATA_PATH = {
    'ROOT': Path('./data/save_data/'),
    'PAGE': lambda page: Path(f'./data/save_data/page_{str(page)}/'),
    'PAGE_SOURCE': lambda page: Path(f'./data/save_data/page_{str(page)}/page_source.json'),
    'DATA': lambda page: Path(f'./data/save_data/page_{str(page)}/data.json'),
}

# CHECK HTML PAGE SOURCE
CHECK_FORMATTED_PAGE_SOURCE_PATH = Path('./check_page_source/formatted.html')


# DRIVER
DRIVER_PATH = lambda num: Path(f'/Users/hoangvinh/OneDrive/Workspace/Support/Driver/chromedriver-mac-x64_{str(num)}/chromedriver')


# UPDATE TIME
UPDATE_TIME = 0