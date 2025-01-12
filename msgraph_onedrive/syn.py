from msgraph_onedrive.operations import download_file, list_folder_children, upload_file, search_file_id
from shared.globals import CHECKPOINTS_PATH
import dotenv
import os
import json
from shared.colorful import print_banner_colored

dotenv.load_dotenv()
def update_crawl_info():
    upload_file(os.getenv('FOLDER_STORAGE_ID'), CHECKPOINTS_PATH['CRAWL'].name, file_path=CHECKPOINTS_PATH['CRAWL'], type='replace')
    print_banner_colored('Upload crawl info thành công', 'success')

def update_extract_info():
    upload_file(os.getenv('FOLDER_STORAGE_ID'), CHECKPOINTS_PATH['EXTRACT'].name, file_path=CHECKPOINTS_PATH['EXTRACT'], type='replace')
    print_banner_colored('Upload extract info thành công', 'success')


def update_link_list():
    upload_file(os.getenv('FOLDER_STORAGE_ID'), CHECKPOINTS_PATH['LINK_LIST'].name, file_path=CHECKPOINTS_PATH['LINK_LIST'], type='replace')
    print_banner_colored('Upload link list thành công', 'success')


def pull_from_onedrive():
    previous_crawl_info = search_file_id(CHECKPOINTS_PATH['CRAWL'].name, folder_id=os.getenv('FOLDER_STORAGE_ID'))
    previous_extract_info = search_file_id(CHECKPOINTS_PATH['EXTRACT'].name, folder_id=os.getenv('FOLDER_STORAGE_ID'))
    previous_link_list = search_file_id(CHECKPOINTS_PATH['LINK_LIST'].name, folder_id=os.getenv('FOLDER_STORAGE_ID'))

    previous_crawl_info_data = download_file(previous_crawl_info)
    previous_extract_info_data = download_file(previous_extract_info)
    previous_link_list_data = download_file(previous_link_list)

    with open(CHECKPOINTS_PATH['CRAWL'].name, 'wb') as file:
        json.dump(previous_crawl_info_data, file)
    with open(CHECKPOINTS_PATH['EXTRACT'].name, 'wb') as file:
        json.dump(previous_extract_info_data, file)
    with open(CHECKPOINTS_PATH['LINK_LIST'].name, 'wb') as file:
        json.dump(previous_link_list_data, file)


def push_all_to_onedrive():
    update_crawl_info()
    update_extract_info()
    update_link_list()

# push_all_to_onedrive()