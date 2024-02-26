import requests
from bs4 import BeautifulSoup
import re
import os

class LinkParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_links_from_file(self):
        links_dict = {}
        with open(self.file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(' - ')
                if len(parts) == 2:
                    topic, url = parts
                    links_dict[topic] = url
        return links_dict

    def parse_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            clean_text = soup.get_text()
            clean_text = re.sub(r'\s+', ' ', clean_text)
            return clean_text
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            return None

    def parse_info_from_file(self,file_path,topics_list):
        data = {}
        with open(file_path, 'r') as file:
            lines = file.readlines()
            key = None
            value = ''
            for line in lines:
                if line.strip():
                    if key is None:
                        key = line.strip()
                    else:
                        value += line
                else:
                    if key is not None:
                        data[key] = value.strip()
                        topics_list+=[key]
                        key = None
                        value = ''
        # Добавляем последний элемент
        if key is not None:
            data[key] = value.strip()
            topics_list+=[key]
        return data

    def parse_all_files_in_directory(self,directory, parsed_data, topics_list):
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.txt'):  # Проверяем, что файл имеет расширение .txt
                    file_data = self.parse_info_from_file(file_path,topics_list)
                    parsed_data.update(file_data)

    
    def add_additional_links(self, parsed_data, topics_list):
        self.parse_all_files_in_directory('./data',parsed_data,topics_list)
    
    def parse_all_pages(self):
        parsed_data = {}
        links_dict = self.read_links_from_file()
        topics_list = []
        for topic, url in links_dict.items():
            text = self.parse_page(url)
            if text:
                parsed_data[topic] = url + text
                topics_list+=[topic]
        self.add_additional_links(parsed_data,topics_list)
        return topics_list,parsed_data


# file_path = 'links.txt'  # путь к файлу с ссылками
# link_parser = LinkParser(file_path)
# all_text = link_parser.parse_all_pages()
# print(all_text)
