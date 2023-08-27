import time
from typing import List, Dict

from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import pandas as pd
from jupyterlab_server import slugify
import concurrent.futures
from configs.config import FANPAGE_FACEBOOK_URL, SPREADSHEET_ID
from services.font_service import FontService
from services.image_service import ImageService
from services.key_service import KeyService
from services.link_service import LinkService
from services.message_service import MessageService
from services.tag_service import TagService


# %%
class Font:
    def __init__(self, name, keys, links, images, post_link, messages, tags, description):
        self.name: str = name
        self.keys: list = keys
        self.slug: str = slugify(self.name)
        self.links: list = links
        self.images: list = images
        self.post_link: str = post_link
        self.messages: list = messages
        self.tags: list = tags
        self.description = description
        self.status = True

    def __str__(self):
        return f'Name: {self.name}\nKeys: {self.keys}\nLinks: {self.links}\nImages: {self.images}\nPost link: {self.post_link}\nMessages: {self.messages}\nTags: {self.tags}\nDescription: {self.description}'


def flatten_2d_string_array(array):
    if array is None:
        return []
    result = []
    for row in array:
        for item in row:
            result.append(item)
    return result


# %%
class GoogleSheetsReader:
    def __init__(self):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        key_file = os.path.join(os.path.dirname(__file__), '../bot', '..', 'keys', 'nvnfont.json')
        credentials = service_account.Credentials.from_service_account_file(key_file, scopes=scopes)
        self.service = build('sheets', 'v4', credentials=credentials)
        self.spreadsheet_id = SPREADSHEET_ID
        self.df = pd.DataFrame()

    def update_data(self, key_service: KeyService, tag_service: TagService, link_service: LinkService,
                    image_service: ImageService, message_service: MessageService, font_service: FontService):
        start_time = time.time()
        result = self.get_result()
        fonts = result['fonts']

        def create_keys():
            return {key.name: key for key in key_service.create_multiple_keys(result['unique_keys'])}

        def create_tags():
            return {tag.name: tag for tag in tag_service.create_multiple_tags(result['unique_tags'])}

        def create_links():
            return {link.url: link for link in link_service.create_multiple_links(result['unique_links'])}

        def create_images():
            return {image.url: image for image in image_service.create_multiple_images(result['unique_images'])}

        def create_messages():
            return {message.value: message for message in
                    message_service.create_multiple_messages(result['unique_messages'])}

        # Tạo ThreadPoolExecutor với 5 luồng đồng thời
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            key_dict = executor.submit(create_keys).result()
            link_dict = executor.submit(create_links).result()
            image_dict = executor.submit(create_images).result()
            message_dict = executor.submit(create_messages).result()
            tag_dict = executor.submit(create_tags).result()
        font_data_list: List[Dict] = []
        for font in fonts:
            font_data = {
                'name': font.name,
                'post_link': font.post_link,
                'slug': font.slug,
                'description': font.description,
                'status': font.status,
                'keys': [key_dict[key] for key in font.keys],
                'links': [link_dict[link] for link in font.links],
                'images': [image_dict[image] for image in font.images],
                'messages': [message_dict[message] for message in font.messages],
                'tags': [tag_dict[tag] for tag in font.tags]
            }
            font_data_list.append(font_data)
        font_service.create_multiple_fonts(font_data_list)
        return f'Updated in {time.time() - start_time} seconds'

    def get_data_as_dataframe(self, sheet_name):
        result = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=sheet_name).execute()
        values = result.get('values', [])
        df = pd.DataFrame(values[1:], columns=values[0])
        return df

    def get_first_sheet_name(self):
        spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        sheet_properties = spreadsheet['sheets']
        return sheet_properties[0]['properties']['title']

    def get_data_first_sheet(self):
        sheet_name = self.get_first_sheet_name()
        self.df = self.get_data_as_dataframe(sheet_name)
        self.df = self.df.fillna('')
        return self.df

    def get_image_unique(self) -> list:
        images = set()
        image_check = flatten_2d_string_array(self.df['Images'].str.split('\n'))
        for image in image_check:
            image = image.strip()
            if image != '':
                images.add(image)
        return list(images)

    def get_link_unique(self) -> list:
        links = set()
        link_check = flatten_2d_string_array(self.df['Links'].str.split('\n'))
        for link in link_check:
            link = link.strip()
            if link != '':
                links.add(link)
        return list(links)

    def get_message_unique(self) -> list:
        messages = set()
        message_check = flatten_2d_string_array(self.df['Messages'].str.split('----end----'))
        for message in message_check:
            message = message.strip()
            if message != '':
                messages.add(message)
        return list(messages)

    def get_tag_unique(self) -> list:
        tags = set()
        tag_check = flatten_2d_string_array(self.df['Tags'].str.split('\n'))
        for tag in tag_check:
            tag = tag.strip()
            if tag != '':
                tags.add(tag)
        return list(tags)

    def get_result(self) -> dict:
        self.get_data_first_sheet()
        unique_keys = set()
        unique_keys_lower = set()
        unique_images = self.get_image_unique()
        unique_links = self.get_link_unique()
        unique_messages = self.get_message_unique()
        unique_tags = self.get_tag_unique()
        fonts = []
        for index, row in self.df.iterrows():
            # Name	Keys	Links	Images	Post_Link	Messages	Tags	Description
            name = row.get('Name')
            if name == '':
                continue
            post_link = row.get('Post_Link') if row.get('Post_Link') != '' else FANPAGE_FACEBOOK_URL
            description = row.get('Description') if row.get('Description') != '' else 'Không có mô tả'
            keys_temp = row.get('Keys').split('\n')
            keys = []
            links = [link.strip() for link in row.get('Links').split('\n') if link.strip() != '']
            images = [image.strip() for image in row.get('Images').split('\n') if image.strip() != '']
            messages = [message.strip() for message in row.get('Messages').split('----end----') if
                        message.strip() != '']
            tags = [tag.strip() for tag in row.get('Tags').split('\n') if tag.strip() != '']
            for key in keys_temp:
                if key != '':
                    if key.lower() not in unique_keys_lower:
                        unique_keys_lower.add(key.lower())
                        unique_keys.add(key)
                        keys.append(key)
            font = Font(name, keys, links, images, post_link, messages, tags, description)
            fonts.append(font)
        return {
            'fonts': fonts,
            'unique_keys': list(unique_keys),
            'unique_images': unique_images,
            'unique_links': unique_links,
            'unique_messages': unique_messages,
            'unique_tags': unique_tags
        }
