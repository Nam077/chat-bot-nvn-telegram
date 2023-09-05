import os
import re
import time

import requests
from slugify import slugify


def get_ktoken():
    base_url = "https://snapsave.io/en52"
    try:
        response = requests.get(base_url)
        data = response.text
        if data:
            token_match = re.search(r'var k__token="([a-f0-9]+)";', data)
            time_match = re.search(r'var k_time="([0-9]+)";', data)
            if token_match and time_match:
                k__token = token_match.group(1)
                k_time = time_match.group(1)
                return k__token, k_time
    except Exception as error:
        return None, None


def check_url(url):
    pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return re.match(pattern, url)


class YoutubeMusicConverter:
    def __init__(self):
        self.url = ""
        self.vt = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }

    def set_url(self, url):
        self.url = url

    def set_vt(self, vt):
        self.vt = vt

    def get_option_download(self):
        k__token, k_time = get_ktoken()
        base_url = "https://snapinsta.io/api/ajaxSearch"
        body = {
            "k_token": k__token,
            "k_exp": k_time,
            "q": self.url,
            "vt": self.vt
        }
        try:
            response = requests.post(base_url, data=body, headers=self.headers)
            data = response.json()
            if not data.get("mess"):
                title = data.get("title")
                links = self.vt == "mp3" and list(data.get("links").get("mp3").values()) or list(
                    data.get("links").get("mp4").values())
                token = data.get("token")
                vid = data.get("vid")
                time_expires = data.get("timeExpires")
                fn = data.get("fn")
                return {
                    "title": title,
                    "links": links,
                    "token": token,
                    "vid": vid,
                    "timeExpires": time_expires,
                    "fn": fn
                }
        except Exception as error:
            print(error)

    def delay(self, ms):
        time.sleep(ms / 1000)

    def get_download_url(self, option_download_data, chose):
        base_url = "https://backend.svcenter.xyz/api/convert-by-45fc4be8916916ba3b8d61dd6e0d6994"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/",
            "Origin": "https://snapinsta.io",
            "Referer": "https://snapinsta.io/",
            "X-Requested-Key": "de0cfuirtgf67a"
        }
        body = {
            "v_id": option_download_data.get("vid"),
            "ftype": chose.get("f"),
            "fquality": chose.get("k"),
            "token": option_download_data.get("token"),
            "timeExpire": option_download_data.get("timeExpires"),
            "client": "SnapInsta.io"
        }
        try:
            response = requests.post(base_url, data=body, headers=headers)
            if response.status_code == 200:
                if self.vt == "mp3":
                    return {
                        "url": response.json().get("d_url"),
                        "title": option_download_data.get("title"),
                        "quality": chose.get("q"),
                        "file_extension": chose.get("f"),
                        "filename": slugify(f"{option_download_data.get('title')}_{chose.get('k')}") + "." + chose.get(
                            "f")
                    }
                elif response.json().get("c_status") == "ok":
                    server = response.json().get("c_server")
                    return self.get_download_url_2_next(option_download_data, chose, server)
        except Exception as error:
            print("Error:", error)

    def get_download_url_2_next(self, option_download_data, chose, server):
        base_url = f"{server}/api/json/convert"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/",
            "Origin": "https://snapinsta.io",
            "Referer": "https://snapinsta.io/",
            "X-Requested-Key": "de0cfuirtgf67a"
        }
        body = {
            "v_id": option_download_data.get("vid"),
            "ftype": chose.get("f"),
            "fquality": chose.get("k"),
            "token": option_download_data.get("token"),
            "timeExpire": option_download_data.get("timeExpires"),
            "fname": option_download_data.get("fn")
        }
        try:
            response = requests.post(base_url, data=body, headers=headers)
            if response.status_code == 200:
                if response.json().get("statusCode") == 300:
                    print("Converting...")
                    self.delay(5000)  # Wait for 5 seconds
                    self.get_download_url_2_next(option_download_data, chose, server)
                else:
                    # self.download(response.json().get("result"), option_download_data.get("title"), chose.get("q"),
                    #               chose.get("f"))
                    return {
                        "url": response.json().get("result"),
                        "title": option_download_data.get("title"),
                        "quality": chose.get("q"),
                        "file_extension": chose.get("f"),
                        "filename": slugify(f"{option_download_data.get('title')}_{chose.get('k')}") + "." + chose.get(
                            "f")
                    }
        except Exception as error:
            pass

    def download(self, url, title, quality, file_extension):
        download_folder = "downloads"
        if not os.path.exists(download_folder):
            os.mkdir(download_folder)
        print(f"Downloading {title}...")
        file_name = slugify(f"{title}_{quality}") + "." + file_extension
        print(file_name)
        response = requests.get(url, headers=self.headers)
        file_path = os.path.join(download_folder, file_name)
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded {file_name} successfully to {download_folder}")

    def enter_url(self):
        url = input("Enter url: ")
        self.set_url(url)


if __name__ == "__main__":
    youtube_music_converter = YoutubeMusicConverter()
    youtube_music_converter.url = 'https://www.youtube.com/watch?v=fyMgBQioTLo'
    youtube_music_converter.vt = 'mp4'
    option_download = youtube_music_converter.get_option_download()
    print(option_download.get('links'))
    option_pick = option_download.get('links')[0]
    print(str(option_pick))
