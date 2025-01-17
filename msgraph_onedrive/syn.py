from msgraph_onedrive.operations import download_file, list_folder_children, upload_file, search_file_id
from shared.globals import CHECKPOINTS_PATH, CHECKPOINTS_PATH_TEST
import dotenv
import os
import json
from shared.colorful import print_banner_colored

dotenv.load_dotenv()
def update_crawl_info(PATH):
    upload_file(os.getenv(PATH['FOLDER_STORAGE_ID_ENV_NAME']), PATH['CRAWL'].name, file_path=PATH['CRAWL'], type='replace')
    print_banner_colored('Upload crawl info thành công', 'success')

def update_extract_info(PATH):
    upload_file(os.getenv(PATH['FOLDER_STORAGE_ID_ENV_NAME']), PATH['EXTRACT'].name, file_path=PATH['EXTRACT'], type='replace')
    print_banner_colored('Upload extract info thành công', 'success')


def update_link_list(PATH):
    upload_file(os.getenv(PATH['FOLDER_STORAGE_ID_ENV_NAME']), PATH['LINK_LIST'].name, file_path=PATH['LINK_LIST'], type='replace')
    print_banner_colored('Upload link list thành công', 'success')


def pull_from_onedrive(PATH):
    previous_crawl_info = search_file_id(PATH['CRAWL'].name, folder_id=os.getenv(PATH['FOLDER_STORAGE_ID_ENV_NAME']))
    previous_extract_info = search_file_id(PATH['EXTRACT'].name, folder_id=os.getenv(PATH['FOLDER_STORAGE_ID_ENV_NAME']))
    previous_link_list = search_file_id(PATH['LINK_LIST'].name, folder_id=os.getenv(PATH['FOLDER_STORAGE_ID_ENV_NAME']))

    previous_crawl_info_data = download_file(previous_crawl_info)
    previous_extract_info_data = download_file(previous_extract_info)
    previous_link_list_data = download_file(previous_link_list)

    with open(PATH['CRAWL'].name, 'wb') as file:
        json.dump(previous_crawl_info_data, file)
    with open(PATH['EXTRACT'].name, 'wb') as file:
        json.dump(previous_extract_info_data, file)
    with open(PATH['LINK_LIST'].name, 'wb') as file:
        json.dump(previous_link_list_data, file)


def push_all_to_onedrive(web):
    # Kiem tra lại là xài test hay xài thường
    # PATH = CHECKPOINTS_PATH[web.upper()]
    PATH = CHECKPOINTS_PATH_TEST[web.upper()]

    update_crawl_info(PATH)
    update_extract_info(PATH)
    update_link_list(PATH)

if __name__ == '__main__':
    pass
    # push_all_to_onedrive('BATDONGSAN')