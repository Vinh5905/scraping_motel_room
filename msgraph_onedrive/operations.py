import os
import dotenv
import httpx
from pathlib import Path
import json
import time
import pickle
import requests
import random
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

    # try:
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

    # except:
    #     if try_again:
    #         raise ValueError('Something wrong!!! (not by authorization)')

    #     print('Try to get access token again!!!')
    #     time.sleep(2)
    #     wrapper(*args, try_again=True, **kwargs)

    return wrapper


@decorator_access_token
def list_folder_children(headers, folder_id=None):
    url = f'{MS_GRAPH_BASE_URL}/me/drive/root/children'

    if folder_id:
        url = f'{MS_GRAPH_BASE_URL}/me/drive/items/{folder_id}/children'

    response = httpx.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return [item for item in data['value']]
    else:
        print(f'Failed list_folder_children : {response.status_code} {response.reason_phrase}')
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
    response = httpx.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        data = response.json()
        return data
    else:
        print(f'Failed create_folder : {response.status_code} {response.reason_phrase}')
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
            response = httpx.put(url, headers=headers, data=file, params=params)
    elif data_upload is not None:
        # print(data_upload)
        response = httpx.put(url, headers=headers, json=data_upload, params=params)
    else:
        print(f'No data or file to upload!!')
        return {}
    
    # Replace -> 200 OK  /  New -> 201 Created
    if response.status_code in (200, 201):
        data = response.json()
        return data
    else:
        print(f'Failed upload_file : {response.status_code} {response.reason_phrase}')
        return {}


@decorator_access_token
def upload_img(headers, folder_id, filename, link_img, type='fail'):
    url = f'{MS_GRAPH_BASE_URL}/me/drive/items/{folder_id}:/{filename}:/content'

    headers = {
        # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Content-Type': 'application/octet-stream',  # For binary,
        **headers
    }

    params = {
        '@microsoft.graph.conflictBehavior': type
    }

    # response_get_img = httpx.get(link_img, headers=headers)
    response_get_img = httpx.get(link_img, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Content-Type': 'application/octet-stream'
    })
    # while True:
    #     proxy = random.choice(PROXIES_LIST)
    #     try:
    #         with httpx.Client(proxy=f'http://{proxy}') as client:
    #             print("COME INSIDE")
    #             response_get_img = client.get('http://ipinfo.io/json', timeout=20)
    #             print(response_get_img.status_code)
    #             print(f"SUCESSFULL {proxy}")
    #             break
    #     except Exception as e:
    #         print(f'ERROR: {e}')
    #         time.sleep(2)

    if response_get_img.status_code == 200: 
        img_data = response_get_img.content
        response_upload = httpx.put(url, headers=headers, params=params, data=img_data)
        if response_upload.status_code in (200, 201):
            data = response_upload.json()
            return data
        else:
            print(f'Failed upload_file : {response_upload.status_code} {response_upload.reason_phrase}')
            return {}
    else:
        # print(f'Failed get content img : {response_get_img.status_code} {response_get_img.reason_phrase}')
        print(f'Fail get img content : {response_get_img.status_code}!!!')
        return {}


@decorator_access_token
def download_file(headers, file_id):
    url = f'{MS_GRAPH_BASE_URL}/me/drive/items/{file_id}/content'

    response = httpx.get(url, headers=headers)

    # Khi download về thường là dạng binary chứ không phải json
    # File found -> 302
    if response.status_code == 302:
        loc = response.headers['location']
        response = httpx.get(loc)
        return (True, response.json())
    elif response.status_code == 200:
        return (True, response.json())
    else:
        print(f'Failed download_file : {response.status_code} {response.reason_phrase}')
        return (False, {})


@decorator_access_token
def search_file_id(headers, name, folder_id=None):
    url = f"{MS_GRAPH_BASE_URL}/me/drive/search(q='{name}')"

    if folder_id:
        url = f"{MS_GRAPH_BASE_URL}/me/drive/items/{folder_id}/search(q='{name}')"
    
    response = httpx.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['value'][0]['id']
    else:
        print(f'Failed search_file_id : {response.status_code} {response.reason_phrase}')
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
dotenv.load_dotenv()
print(upload_img(os.getenv('FOLDER_IMG_STORAGE_ID'), 'img_1.jpg', 'https://file4.batdongsan.com.vn/resize/1275x717/2024/10/31/20241031094536-e507_wm.jpg'))