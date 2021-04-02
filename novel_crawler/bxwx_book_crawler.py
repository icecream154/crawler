import concurrent
import concurrent.futures
from novel_crawler.abstract_book_crawler import AbstractBookCrawler
from bs4 import BeautifulSoup
from utils.content_filter import content_filter
import requests


class BxwxBookCrawler(AbstractBookCrawler):

    def __init__(self, book_root_url: str, save_path='./', max_workers=5):
        super().__init__(book_root_url, save_path)
        html_text = requests.get(self.book_root_url).text
        self.phrase_soup = BeautifulSoup(html_text, 'lxml')
        fault_block = self.phrase_soup.find('div', class_='blocktitle')
        if fault_block is not None:
            print("root_url [%s] doesn't exist, book crawler init failed" % book_root_url)
            self.valid = False
            return

        self.book_name = BxwxBookCrawler.get_book_name(self.phrase_soup)
        self.book_author = BxwxBookCrawler.get_author_name(self.phrase_soup)
        self.chapter_list = BxwxBookCrawler.get_chapter_list(self.phrase_soup, self.book_root_url)
        self.book_save_path = save_path + self.book_name + '-' + self.book_author + '.txt'
        self.max_workers = max_workers
        self.valid = True
        print('book crawler [%s] init success' % (self.book_name + '-' + self.book_author))

    @staticmethod
    def get_book_name(phrase_soup):
        book_meta_data = phrase_soup.find('div', id='info').h1.text.split(' / ')
        book_name = book_meta_data[0]
        return book_name

    @staticmethod
    def get_author_name(phrase_soup):
        book_meta_data = phrase_soup.find('div', id='info').h1.text.split(' / ')
        book_author = book_meta_data[1]
        return book_author

    @staticmethod
    def get_chapter_list(phrase_soup, book_root_url):
        chapter_list = []

        # find all chapters
        chapter_list_dl = phrase_soup.find('dl', class_='zjlist')
        curr_chapter_id = 0
        for chapter_dd in chapter_list_dl.find_all('dd'):
            chapter_link = chapter_dd.a;
            if chapter_link is not None:
                # update current chapter id
                curr_chapter_id += 1
                # add relative url to the root url and phrase the html text
                chapter_url = book_root_url + chapter_dd.a.get('href')
                chapter_list.append((chapter_link.text, chapter_url))

        return chapter_list

    def crawl_chapter(self, start_c_id=1, end_c_id=-1):
        if end_c_id < 0:  # keep crawling until the final chapter
            end_c_id = len(self.chapter_list)

        if end_c_id < start_c_id: return  # invalid request

        with open(self.book_save_path, 'a+') as save_file:
            for c_id in range(start_c_id, end_c_id + 1):
                self.save_chapter(c_id, BxwxBookCrawler.get_html_text(self.chapter_list[c_id - 1][1]), save_file)

    def crawl_chapter_with_executors(self, start_c_id=1, end_c_id=-1):
        if end_c_id < 0:  # keep crawling until the final chapter
            end_c_id = len(self.chapter_list)

        if end_c_id < start_c_id: return  # invalid request

        chapter_list = self.chapter_list[start_c_id - 1: end_c_id]
        content_dict = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(BxwxBookCrawler.get_html_text, url[1]): url for url in chapter_list}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))
                else:
                    # print('[%s] fetch success' % url)
                    content_dict[url[1]] = data

        with open(self.book_save_path, 'a+') as save_file:
            for c_id in range(start_c_id, end_c_id + 1):
                try:
                    chapter_html_text = content_dict[self.chapter_list[c_id - 1][1]]
                    self.save_chapter(c_id, chapter_html_text, save_file)
                except KeyError as e:
                    print('content of url [%s] not found, try again ... ' % self.chapter_list[c_id - 1][1])
                    chapter_html_text = BxwxBookCrawler.get_html_text(self.chapter_list[c_id - 1][1])
                    if chapter_html_text is not None:
                        self.save_chapter(c_id, chapter_html_text, save_file)
                        print('request success, chapter saved')
                    else:
                        print('request fail again, skip ... ')

    @staticmethod
    # @time_tracer
    def get_html_text(url, timeout=30):
        return requests.get(url, timeout=timeout).text

    # @time_tracer
    def save_chapter(self, c_id, chapter_html_text, save_file):
        chapter_html_phrase_soup = BeautifulSoup(chapter_html_text, 'lxml')

        # find the div with content of the novel
        content_div = chapter_html_phrase_soup.find('div', id='content')

        # content filter
        replace_list = [('    ', '\n    '),
                        ('笔下文学网 www.bixiawenxue.org，最快更新' + self.book_name + '最新章节！', '\n')]
        chapter_content = content_filter(content_div.text, replace_list)

        # write the formatted content into the text file
        save_file.write('\n')
        # write chapter name
        save_file.write(self.chapter_list[c_id - 1][0])
        # write chapter content
        save_file.write(chapter_content)
        save_file.write('\n')

        # print success message
        if c_id % 200 == 0 or c_id == len(self.chapter_list):
            print('cid[%d/%d][%s] : [%s] done' % (c_id, len(self.chapter_list), self.chapter_list[c_id - 1][1], self.chapter_list[c_id - 1][0]))


if __name__ == '__main__':
    for book_index in range(501, 521):
        print('Task %d start:' % book_index)
        bc = BxwxBookCrawler('https://www.bixiawenxue.org/book_' + str(book_index) + '/', '~/Documents/novs/', 150)
        if bc.valid:
            bc.crawl_chapter_with_executors()

