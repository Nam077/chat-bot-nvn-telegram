import requests
import json


class SoundCloudDownloader:
    def __init__(self):
        self.base_url = 'https://api.downloadsound.cloud/track'
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'vi,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/json;charset=UTF-8',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'Referer': 'https://downloadsound.cloud/',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }

    def download_track(self, track_url):
        data = {'url': track_url}
        response = requests.post(self.base_url, headers=self.headers, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            return None


