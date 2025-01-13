import os
import dotenv
import httpx
from pathlib import Path
import json
import time
import pickle
import requests
import random
import base64
from msgraph_onedrive.msgraph import get_access_token, MS_GRAPH_BASE_URL
from shared.globals import ACCESS_TOKEN
from shared.colorful import print_banner_colored
from shared.globals import PROXIES_LIST

def decorator_access_token(func):
    def wrapper(*args, try_again=False, **kwargs):
        dotenv.load_dotenv()

        APPLICATION_ID = os.getenv('APPLICATION_ID')
        CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        SCOPES = ['User.Read', 'Files.ReadWrite.All']

        try:
            if try_again:
                access_token = get_access_token(APPLICATION_ID, CLIENT_SECRET, SCOPES)
                with open(ACCESS_TOKEN, 'w') as file:
                    json.dump({
                        'access_token': access_token
                    }, file)
            else:
                with open(ACCESS_TOKEN, 'r') as file:
                    access_token = json.load(file)
                    access_token = access_token['access_token']

            headers = {
                'Authorization': 'Bearer ' + access_token
            }

            data = func(headers, *args, **kwargs)

            if not data:
                raise ValueError('Khong tim thay data response')
            else:
                if isinstance(data, tuple):
                    if data[0] is True:
                        data = data[1]
                    else:
                        raise ValueError('Khong tim thay data response')
                
                return data

        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 403:
                if try_again:
                    raise ValueError('Something wrong!!! (not by authorization)')

                print('Try to get access token again!!!')
                time.sleep(2)
                wrapper(*args, try_again=True, **kwargs)
            else:
                raise
        except Exception as e:
            print(f'ERROR: {e}')
    return wrapper


@decorator_access_token
def list_folder_children(headers, folder_id=None):
    url = f'{MS_GRAPH_BASE_URL}/me/drive/root/children'

    if folder_id:
        url = f'{MS_GRAPH_BASE_URL}/me/drive/items/{folder_id}/children'

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    if response.status_code == 200:
        data = response.json()
        return [item for item in data['value']]
    else:
        print(f'Failed list_folder_children : {response.status_code}')
        return []


@decorator_access_token
def create_folder(headers, name, type='fail', folder_id=None):
    url = f'{MS_GRAPH_BASE_URL}/me/drive/root/children'

    if folder_id:
        url = f'{MS_GRAPH_BASE_URL}/me/drive/items/{folder_id}/children'
    
    payload = {
        'name': name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": type
    }

    # @microsoft.graph.conflictBehavior được coi là một phần của body của yêu cầu
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    if response.status_code == 201:
        data = response.json()
        return data
    else:
        print(f'Failed create_folder : {response.status_code}')
        return {}
    

@decorator_access_token
def upload_file(headers, folder_id, filename, file_path: Path = None, data_upload = None, type='fail'):
    # Upload a new file
    url = f'{MS_GRAPH_BASE_URL}/me/drive/items/{folder_id}:/{filename}:/content'

    # @microsoft.graph.conflictBehavior liên quan đến hành vi xung đột khi file đã tồn tại, không phải nội dung chính của yêu cầu
    params = {
        '@microsoft.graph.conflictBehavior': type
    }

    response = None
    if file_path is not None:
        with open(file_path, 'rb') as file:
            response = requests.put(url, headers=headers, data=file, params=params)
    elif data_upload is not None:
        # print(data_upload)
        response = requests.put(url, headers=headers, json=data_upload, params=params)
    else:
        print(f'No data or file to upload!!')
        return {}
    
    response.raise_for_status()
    # Replace -> 200 OK  /  New -> 201 Created
    if response.status_code in (200, 201):
        data = response.json()
        return data
    else:
        print(f'Failed upload_file : {response.status_code}')
        return {}


@decorator_access_token
def upload_img(headers, folder_id, filename, binary_data, type='fail'):
    url = f'{MS_GRAPH_BASE_URL}/me/drive/items/{folder_id}:/{filename}:/content'

    headers['Content-Type'] = 'application/octet-stream' # For binary

    params = {
        '@microsoft.graph.conflictBehavior': type
    }

    # with open('output.jpg', 'wb') as file:
    #     file.write(binary_data)

    response = requests.put(url, headers=headers, params=params, data=binary_data)
    response.raise_for_status()
    if response.status_code in (200, 201):
        data = response.json()
        return data
    else:
        print(f'Failed upload_file : {response.status_code}')
        return {}


@decorator_access_token
def download_file(headers, file_id):
    url = f'{MS_GRAPH_BASE_URL}/me/drive/items/{file_id}/content'

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    # Khi download về thường là dạng binary chứ không phải json
    # File found -> 302
    if response.status_code == 302:
        loc = response.headers['location']
        response = requests.get(loc)
        return (True, response.json())
    elif response.status_code == 200:
        return (True, response.json())
    else:
        print(f'Failed download_file : {response.status_code}')
        return (False, {})


@decorator_access_token
def search_file_id(headers, name, folder_id=None):
    url = f"{MS_GRAPH_BASE_URL}/me/drive/search(q='{name}')"

    if folder_id:
        url = f"{MS_GRAPH_BASE_URL}/me/drive/items/{folder_id}/search(q='{name}')"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    if response.status_code == 200:
        data = response.json()
        return data['value'][0]['id']
    else:
        print(f'Failed search_file_id : {response.status_code}')
        return {}



def get_access_token_for_current():
    dotenv.load_dotenv()

    APPLICATION_ID = os.getenv('APPLICATION_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    SCOPES = ['User.Read', 'Files.ReadWrite.All']

    access_token = get_access_token(APPLICATION_ID, CLIENT_SECRET, SCOPES)

    return access_token

# print(get_access_token_for_current())
# print(upload_img())
'''
https://file4.batdongsan.com.vn/resize/1275x717/2024/10/31/20241031094536-e507_wm.jpg
https://file4.batdongsan.com.vn/resize/1275x717/2024/10/31/20241031094541-cc2f_wm.jpg
https://file4.batdongsan.com.vn/resize/1275x717/2024/10/31/20241031094541-cfdc_wm.jpg
https://file4.batdongsan.com.vn/resize/1275x717/2024/10/31/20241031094541-8c0e_wm.jpg
https://file4.batdongsan.com.vn/resize/1275x717/2024/10/31/20241031094542-6678_wm.jpg
https://file4.batdongsan.com.vn/resize/1275x717/2024/10/31/20241031094542-c1dd_wm.jpg
https://file4.batdongsan.com.vn/resize/1275x717/2024/10/31/20241031094543-1e5b_wm.jpg
https://file4.batdongsan.com.vn/resize/1275x717/2024/10/31/20241031094543-18cb_wm.jpg
https://file4.batdongsan.com.vn/resize/1275x717/2024/10/31/20241031094544-dbc0_wm.jpg
'''

