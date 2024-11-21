# https://www.notion.so/Crawl-data-12b2ecc42aa5807285fedc52bb83df0c?pvs=4

import requests
import threading
from collections import deque

# Check proxy valid by sending request
def check_proxy_valid(proxy, last_time = False):
    link_get_check = 'http://ipinfo.io/json' # Link request to check proxy

    if proxy == '\n': return False
    # Test request with proxy (error then False)
    try:
        res = requests.get(link_get_check, proxies = {
            'https': proxy,
            'http': proxy
        })
    
    except:
        if last_time:
            return False

        return check_proxy_valid(proxy, True)
    
    print('HTTP STATUS CODE: ', res.status_code)
    # If not error, then status_code = 200 show proxy is still working
    return (res.status_code == 200)

def list_valid_proxies(list_proxies, lock, file_valid):
    # Lock to take a proxy from list
    with lock:
        proxy = list_proxies.popleft()
    
    if check_proxy_valid(proxy):
        # Lock when add to file valid
        with lock:
            file_valid.write(proxy + '\n')

        print(f'{proxy} is valid')
    else:
        print(f'{proxy} is NOT valid')

def create_proxies_valid():
    # Link
    link_file_proxies_raw = './proxies/proxies_raw.txt'
    link_file_proxies_valid = './proxies/proxies_valid.txt'
    # Get all proxy from file
    proxies_raw = []
    with open(link_file_proxies_raw, 'r') as file:
        proxies_raw = [proxy.replace('\n', '') for proxy in file.readlines()]

    file_valid = open(link_file_proxies_valid, 'w')

    proxies = deque([])
    proxies_valid = []
    # Add to queue (logic for threading)
    for proxy in proxies_raw:
        proxies.append(proxy)

    # Thread 
    lock = threading.Lock() # Mutex (Lock)

    # Create threads array to call join() for each thread
    threads = []          
    # Create threads
    for _ in range(len(proxies)):
        thread = threading.Thread(target=lambda: list_valid_proxies(proxies, lock, file_valid))
        threads.append(thread)
        thread.start()
    # Block main thread until all thread is done
    for thread in threads: thread.join()

    # Close file valid
    file_valid.close()

if __name__ == '__main__':
    create_proxies_valid()