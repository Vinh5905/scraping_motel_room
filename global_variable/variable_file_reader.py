# Get proxies list
with open('./proxies/proxies_valid.txt', 'r') as file:
    # Use splitlines() to split by lines without \n
    proxies_list = file.read().splitlines()

