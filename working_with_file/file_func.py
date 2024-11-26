import json
from pathlib import Path

def save_data(data):
    path_data = Path('./working_with_file/save_data/data.json')
    path_page_source = Path('./working_with_file/save_data/page_source.json')

    # Save data crawl
    data_to_save = data['data']
    merged_data = []

    if path_data.exists():
        with open(path_data, 'r') as file:
            try:
                all_data = json.load(file)
            except:
                all_data = []
            
            merged_data.extend(all_data)
    
    merged_data.append(data_to_save)

    with open(path_data, 'w') as file:
        json.dump(merged_data, file, ensure_ascii=False)

    # Save page source
    page_source_to_save = {
        'productId': data_to_save['productId'],
        'page_source': data['page_source']
    }

    merged_page_source = []

    if path_page_source.exists():
        with open(path_page_source, 'r') as file:
            try:
                all_data = json.load(file)
            except:
                all_data = []
            
            merged_page_source.extend(all_data)
    
    merged_page_source.append(page_source_to_save)

    with open(path_page_source, 'w') as file:
        json.dump(merged_page_source, file, ensure_ascii=False)
    