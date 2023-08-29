import os
import requests
import json
import re
from urllib.parse import urlparse

from fontTools import ttLib


class FontshopTypeface:
    def __init__(self, name):
        self.name = name
        self.fonts = []
        self.fonts_available = 0


class FontshopFont:
    def __init__(self, font_name, weight_name, font_id, available):
        self.font_name = font_name
        self.weight_name = weight_name
        self.font_id = font_id
        self.available = available


class Constants:
    BASE_URL = "https://www.fontshop.com/search_data.json?search_mode=families&q={0}&size=1&fields=typeface_data,opentype_features"
    BASE_CSS = "https://www.fontshop.com/webfonts/{0}.css"
    CDN_REGEX = "(fast[^']*)"


def get_font_information(url):
    try:
        download_url = url
        if download_url.hostname != "www.fontshop.com":
            raise Exception()

        response = requests.get(Constants.BASE_URL.format(url.path.split('/')[-1]))
        font_data = response.json()
        # save font data to file
        with open('font_data.json', 'w', encoding='utf-8') as f:
            json.dump(font_data, f)

        typeface_data = font_data['families']['hits']['hits'][0]['_source']
        typeface = FontshopTypeface(typeface_data['clean_name'])

        for font_info in typeface_data['typeface_data']:
            font_available = False
            if font_info.get('webfont') and font_info['webfont'].get('url'):
                font_available = True

            font = FontshopFont(font_info['name'], font_info['weight_name'], font_info['layoutfont_id'], font_available)
            typeface.fonts.append(font)

        typeface.fonts_available = sum(1 for font in typeface.fonts if font.available)

        return typeface

    except Exception as e:
        print("Could not get font information:", e)
        return None


def download_font_files(typeface, save_to_path):
    regex = re.compile(Constants.CDN_REGEX)
    percent_progress = 1

    for font in typeface.fonts:
        if font.available:
            css_url = Constants.BASE_CSS.format(font.font_id)
            css_response = requests.get(css_url)
            cdn_url = "https://" + regex.search(css_response.text).group()

            headers = {"referer": "https://www.fontshop.com/"}
            font_file = requests.get(cdn_url, headers=headers, stream=True)
            font_data = font_file.content

            font_woff_path = os.path.join(save_to_path, f"{font.font_name}.woff")
            with open(font_woff_path, "wb") as f:
                f.write(font_data)

            print(
                f"Downloaded and converted {percent_progress}/{typeface.fonts_available} font files: {font.font_name}_{font.font_id}.ttf")
            percent_progress += 1


def main():
    font_url = input("Enter the font URL: ")
    save_to_path = 'downloads'

    if not os.path.exists(save_to_path):
        os.makedirs(save_to_path)

    parsed_url = urlparse(font_url)
    font_typeface = get_font_information(parsed_url)

    if font_typeface:
        print(
            f"Loaded {font_typeface.fonts_available}/{len(font_typeface.fonts)} available fonts: {font_typeface.name}")
        download_font_files(font_typeface, save_to_path)
        print("Finished downloading and converting fonts.")


if __name__ == "__main__":
    main()
