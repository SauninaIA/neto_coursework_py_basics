import requests
from datetime import datetime
from pprint import pprint
import json
import os


FILE_CATALOG = 'photos'
LOG_FILE = 'logs.txt'
BASE_PATH = os.getcwd()
FULL_PATH = os.path.join(BASE_PATH, FILE_CATALOG)
FULL_LOGS_PATH = os.path.join(BASE_PATH, LOG_FILE)


def log_func(file_path, data):
    with open(file_path, 'a', encoding='utf-8') as file:
        result = f'{datetime.now()} | {data} \n'
        file.write(result)


with open('token_vk.txt', 'r') as file_object:
    token_vk = file_object.read().strip()


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_albums(self, owner_id):
        info_albums_dict = {}
        get_albums_url = self.url + 'photos.getAlbums'
        get_albums_params = {
            'owner_id': owner_id,
        }
        res = requests.get(get_albums_url, params={**self.params, **get_albums_params}).json()
        data = res['response']['items']
        for album in data:
            info_albums_dict[album['title']] = album['id']
        pprint(info_albums_dict)

    def get_photo(self, owner_id, album_id='profile'):
        info_photo_list = []
        get_photo_url = self.url + 'photos.get'
        get_photo_params = {
            'owner_id': owner_id,
            'album_id': album_id,
            'rev': 0,
            'extended': 1,
            'count': 5
        }
        res = requests.get(get_photo_url, params={**self.params, **get_photo_params}).json()
        data = res['response']['items']
        for photo in data:
            info_photo_dict = {}
            info_photo_dict['file_name'] = f"{photo['likes']['count']}.jpg"
            info_photo_dict['size'] = photo['sizes'][-1]['type']
            info_photo_dict['url'] = photo['sizes'][-1]['url']
            info_photo_dict['date'] = photo[ 'date']
            info_photo_list.append(info_photo_dict)
        with open('info_photo.json', 'w') as file:
            json.dump(info_photo_list, file, ensure_ascii=False, indent=4)
        file_names = []
        for photo in info_photo_list:
            if photo['file_name'] not in file_names:
                file_name = photo['file_name']
            else:
                file_name = f"{photo['file_name']}-{photo['date']}.jpg"
            file_names.append(photo['file_name'])
            response = requests.get(photo['url'])
            with open(os.path.join(FULL_PATH, file_name), 'wb') as file:
                file.write(response.content)
            data = f'Фото {file_name} было сохранено.'
            log_func(FULL_LOGS_PATH, data)
        return


with open('token_yandex.txt', 'r') as file_object:
    token_ya = file_object.read().strip()


class YaUploader:
    def __init__(self, token_ya):
        self.token = token_ya

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def upload(self, disk_file_path: str, file_name: str):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params).json()
        href = response['href']
        photo_name = os.path.join(FULL_PATH, file_name)
        response = requests.put(href, data=open(photo_name, 'rb'))
        response.raise_for_status()
        if response.status_code == 201:
            data = f'Фото {file_name} загружено на Я.Диск.'
            log_func(FULL_LOGS_PATH, data)


if __name__ == '__main__':
    vk_client = VkUser(token_vk, '5.131')
    vk_client.get_albums('...')
    vk_client.get_photo('...', '...')
    uploader = YaUploader(token_ya)
    photos_list = os.listdir(FULL_PATH)
    for photo in photos_list:
        file_name = f'{photo}'
        path_to_file = f'Photos from VK/{file_name}'
        result = uploader.upload(path_to_file, file_name)