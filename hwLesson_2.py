"""
Источник https://geekbrains.ru/posts/
Необходимо обойти все записи в блоге и извлеч из них информацию следующих полей:
url страницы материала
Заголовок материала
Первое изображение материала
Дата публикации (в формате datetime)
имя автора материала
ссылка на страницу автора материала
пример словаря:
{
"url": "str",
"title": "str",
"image": "str",
"writer_name": "str",
"writer_url": "str",
"pub_date": datetime object,
}
"""

import requests
import bs4
from pymongo import MongoClient


class ParserPost:
    url_base = 'https://geekbrains.ru'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    }
    url_old = set()
    url_new = set()
    url_post = set()
    db_client = MongoClient('mongodb://localhost:27017')

    def get_soup(self, url):
        response = requests.get(url, headers=self.headers)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        self.url_old.add(url)
        return soup

    def get_pages(self, soup):
        ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        li = ul.find_all('li')
        target = set()
        for itm in li:
            if itm.find('a').attrs.get('href'):
                target.add(f'{self.url_base}{itm.find("a").attrs.get("href")}')
        return target

    def get_post_url(self, soup):
        wrapper = soup.find('div', attrs={'class': "post-items-wrapper"})
        posts = wrapper.find_all('div', attrs={'class': "post-item"})
        target = set()
        for itm in posts:
            if itm.find('a').attrs.get('href'):
                target.add(f'{self.url_base}{itm.find("a").attrs.get("href")}')
        return target

    def get_target_info(self):
        for itm in self.url_post:
            soup = self.get_soup(itm)
            url = itm
            title = soup.find('h1', attrs={'itemprop': 'headline'}).string
            image = soup.find('img').attrs.get('src')
            writer_name = soup.find('div', attrs={'itemprop': 'author'}).string
            pub_date = soup.find('time').attrs.get('datetime')
            self.save_to_db(
                {
                    'url': url,
                    'title': title,
                    'image': image,
                    'writer_name': writer_name,
                    'pub_date': pub_date,
                }
            )

    def save_to_db(self, data: dict):
        db = self.db_client['GeekBrainsHomeWorkLesson2']
        collection = db['Posts']
        collection.insert_one(data)

    def parse(self):
        url = f'{self.url_base}/posts'
        while url:
            soup = self.get_soup(url)
            self.url_new.update(self.get_pages(soup))
            self.url_new.difference_update(self.url_old)
            if self.url_new:
                url = self.url_new.pop()
            else:
                url = None
            self.url_post.update(self.get_post_url(soup))
        self.get_target_info()
        print(1)


if __name__ == '__main__':
    obj = ParserPost()
    obj.parse()
