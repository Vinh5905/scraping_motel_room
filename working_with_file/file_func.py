import json
from pathlib import Path
from bs4 import BeautifulSoup

'''
Save theo dạng :

save_data
    |--- data
        |--- page_1
                |--- page_source.json
                |--- data.json
        |--- page_2
        |--- page_{...}
    |--- previous_extract_info.json
    |--- previous_crawl_info.json

'''
def save_page_source(page, data):
    path_data = Path('./working_with_file/save_data/data')
    path_data.mkdir(exist_ok=True)

    path_page_folder = path_data / f'page_{str(page)}'
    path_page_folder.mkdir(exist_ok=True)

    path_page_source_save = path_page_folder / 'page_source.json'

    merged_page_source = {}

    if path_page_source_save.exists():
        with open(path_page_source_save, 'r') as file:
            try:
                all_data = json.load(file)
            except:
                all_data = {}
            
            merged_page_source.update(all_data)
    
    merged_page_source[data['link']] = data['page_source']

    with open(path_page_source_save, 'w') as file:
        json.dump(merged_page_source, file, ensure_ascii=False)