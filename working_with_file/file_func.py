import json
from pathlib import Path

def add_data_to_csv(self, data):
    path = Path('./working_with_file/save_data/data.csv')
    # merged_data = [data]
    # if path.exists():
    #     with open(path, 'r') as file:
    #         try:
    #             data_in_file = json.load(file)
    #         except:
    #             data_in_file = []
            
    #         merged_data.extend(data_in_file)

    # with open(path, 'w') as file:
    #     json.dump(merged_data, file, ensure_ascii=False)

    # self.link_num += 1
    # self.change_previous_crawl()
    # print('---- LẤY THÀNH CÔNG ----')
    