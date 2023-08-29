import os
import shutil
from concurrent.futures.thread import ThreadPoolExecutor
import pyzipper
import requests
import re
import json
from configs.logging import logger


def extract_font_family_name(url) -> str or None:
    match = re.search(r'/families/([^/?]+)', url)
    if match:
        return match.group(1)
    return None


class FontCrawlerService:
    def __init__(self, crawl_url='', parent_folder='downloads'):
        self.secondary_typefaces = None
        self.primary_typefaces = None
        self.folder_save = None
        self.crawl_url = crawl_url
        self.parent_folder = parent_folder
        self.result_urls = []
        self.folder_name = None

    def set_crawl_url(self, crawl_url):
        self.crawl_url = crawl_url

    def crawl_primary_and_secondary_typefaces(self):
        response = requests.get(self.crawl_url)
        html = response.text
        json_data = re.search(r"var primary_typefaces = (.*?);", html).group(1)
        self.primary_typefaces = json.loads(json_data)

        json_data = re.search(r'var secondary_typefaces = (\[.*?\]);', html).group(1)
        self.secondary_typefaces = json.loads(json_data)

        self.result_urls = [item.get('url') for item in self.secondary_typefaces if 'url' in item]
        if 'url' in self.primary_typefaces:
            self.result_urls.append(self.primary_typefaces['url'])

    def create_save_folder(self) -> bool:
        folder_name = extract_font_family_name(self.crawl_url)
        if not folder_name:
            return False
        self.folder_name = folder_name
        self.folder_save = os.path.join(self.parent_folder, folder_name)
        if not os.path.exists(self.folder_save):
            os.makedirs(self.folder_save)
        return True

    def save_font_data(self) -> str or None:
        check = self.create_save_folder()
        if not check:
            return None

        self.crawl_primary_and_secondary_typefaces()
        prefix = "https://www.fontshop.com"

        if not self.result_urls:
            return None

        def download_font(url, idx):
            test_url = prefix + url
            try:
                response = requests.get(test_url)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.info(f"Error downloading font file from {test_url}: {e}")
                return

            html = response.text
            url_match = re.search(r"url\('([^']*fast\.fonts\.net[^']*)'\)", html)

            if url_match:
                url = url_match.group(1)
                base_url = "https:" + url.split('?')[0]

                try:
                    font_file = requests.get(base_url, stream=True)
                    font_file.raise_for_status()
                except requests.exceptions.RequestException as e:
                    logger.info(f"Error downloading font file from {base_url}: {e}")
                    return

                original_filename = self.folder_name + str(idx) + ".woff"
                save_path = os.path.join(self.folder_save, f"{original_filename}")

                with open(save_path, 'wb') as f:
                    f.write(font_file.content)
                logger.info(f"Saved font file to {save_path}")
            else:
                logger.info(f"Could not find font file url in {test_url}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(download_font, url, idx) for idx, url in enumerate(self.result_urls, start=1)]
            for future in futures:
                future.result()

        return self.create_zip_from_folder()

    def create_zip_from_folder(self):
        zip_filename = f"{self.folder_name}.zip"
        zip_path = os.path.join(self.parent_folder, zip_filename)

        with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
            zf.setpassword(b"nvnfont")
            for root, dirs, files in os.walk(self.folder_save):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.folder_save)
                    zf.write(file_path, rel_path)

        if os.path.exists(self.folder_save):
            shutil.rmtree(self.folder_save)
        return zip_path
