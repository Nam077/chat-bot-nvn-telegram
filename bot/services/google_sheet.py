from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import pandas as pd
from bot.configs.config import FANPAGE_FACEBOOK_URL, SPREADSHEET_ID


# %%
class Font:
    def __init__(self, name, keys, links, images, post_link, messages, tags, description):
        self.name: str = name
        self.keys: list = keys
        self.links: list = links
        self.images: list = images
        self.post_link: str = post_link
        self.messages: list = messages
        self.tags: list = tags
        self.description = description

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
        key_file = os.path.join(os.path.dirname(__file__), '..', '..', 'keys', 'nvnfont.json')
        credentials = service_account.Credentials.from_service_account_file(key_file, scopes=scopes)
        self.service = build('sheets', 'v4', credentials=credentials)
        self.spreadsheet_id = SPREADSHEET_ID
        self.df = pd.DataFrame()

    def get_first_sheet_name(self):
        spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        sheet_properties = spreadsheet['sheets']
        return sheet_properties[0]['properties']['title']

    def get_data_as_dataframe(self, sheet_name):
        result = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=sheet_name).execute()
        values = result.get('values', [])
        df = pd.DataFrame(values[1:], columns=values[0])
        return df

    def get_data_first_sheet(self):
        sheet_name = self.get_first_sheet_name()
        self.df = self.get_data_as_dataframe(sheet_name)
        self.df = self.df.fillna('')
        return self.df

    def get_image_unique(self) -> list:
        images = set()
        image_check = flatten_2d_string_array(self.df['Keys'].str.split('\n'))
        for image in image_check:
            if image != '':
                images.add(image)
        return list(images)

    def get_link_unique(self) -> list:
        links = set()
        link_check = flatten_2d_string_array(self.df['Links'].str.split('\n'))
        for link in link_check:
            if link != '':
                links.add(link)
        return list(links)

    def get_message_unique(self) -> list:
        messages = set()
        message_check = flatten_2d_string_array(self.df['Messages'].str.split('\n'))
        for message in message_check:
            if message != '':
                messages.add(message)
        return list(messages)

    def get_tag_unique(self) -> list:
        tags = set()
        tag_check = flatten_2d_string_array(self.df['Tags'].str.split('\n'))
        for tag in tag_check:
            if tag != '':
                tags.add(tag)
        return list(tags)

    def get_result(self) -> dict:
        self.get_data_first_sheet()
        unique_keys = set()
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
            #     nếu post link ko có thì mặc định là fb.com/nvnfont
            post_link = row.get('Post_Link') if row.get('Post_Link') != '' else FANPAGE_FACEBOOK_URL
            description = row.get('Description') if row.get('Description') != '' else 'Không có mô tả'
            keys_temp = row.get('Keys').split('\n')
            keys = []
            links = [link for link in row.get('Links').split('\n') if link != '']
            images = [image for image in row.get('Images').split('\n') if image != '']
            messages = [message for message in row.get('Messages').split('\n') if message != '']
            tags = [tag for tag in row.get('Tags').split('\n') if tag != '']
            for key in keys_temp:
                if key not in unique_keys:
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


# Cấu hình thông tin truy cập API theo đường dẫn tuyệt đối


# Khởi tạo đối tượng GoogleSheetsReader
