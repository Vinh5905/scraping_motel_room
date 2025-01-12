import json
from pathlib import Path
import csv
from shared.globals import CHECKPOINTS_PATH, ALL_EXTRACTED_DATA_PATH, SAVE_DATA_PATH

def get_data_to_csv():
    path_previous_extract = Path('./data/checkpoints/previous_extract_info.json')
    path_data_csv = Path('./data/all_extracted_data/data.csv')

    all_data = []

    if  not ALL_EXTRACTED_DATA_PATH.parent.exists():
        ALL_EXTRACTED_DATA_PATH.parent.mkdir(exist_ok=True)

    with open(CHECKPOINTS_PATH['EXTRACT'], 'r') as file:
        max_page = int(json.load(file))

    # Get all fields
    all_fields = []

    for i in range(1, max_page):
        path = SAVE_DATA_PATH['DATA'](i)
        if path.exists():
            with open(path, 'r') as file:
                page_data = json.load(file)
            
            for data in page_data:
                all_data.append(data)
                for key in data:
                    if key not in all_fields:
                        all_fields.append(key)

        else:
            continue
    
    with open(ALL_EXTRACTED_DATA_PATH, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=all_fields)
        writer.writeheader()
        writer.writerows(all_data)

if __name__ == '__main__':
    # get_data_to_csv()
    with open(ALL_EXTRACTED_DATA_PATH, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)

        data = list(reader)
    print(data[239])
        


