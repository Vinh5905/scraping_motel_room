from pathlib import Path

proxies_list_path = Path('./proxies/proxies_raw.txt')

# Get proxies list
with open(proxies_list_path, 'r') as file:
    # Use splitlines() to split by lines without \n
    proxies_list = file.read().splitlines()