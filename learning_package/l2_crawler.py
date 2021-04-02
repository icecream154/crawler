from bs4 import BeautifulSoup
import requests


def save_chapter(chapter_id, book_chapter_url, book_name, chapter_name, save_file):
    chapter_html_text = requests.get(book_chapter_url).text
    chapter_html_phrase_soup = BeautifulSoup(chapter_html_text, 'lxml')

    # find the div with content of the novel
    content_div = chapter_html_phrase_soup.find('div', id='content')

    # write the formatted content into the text file
    save_file.write('\n')
    save_file.write(chapter_name)
    chapter_content = content_div.text.replace('    ', '\n    ')
    chapter_content = chapter_content.replace('笔下文学网 www.bixiawenxue.org，最快更新' + book_name + '最新章节！', '\n')
    save_file.write(chapter_content)
    save_file.write('\n')

    # print success message
    print('c_id: [%d] href: [%s] chapter: [%s] done' % (chapter_id, book_chapter_url, chapter_name))


def fetch_book(book_root_url, save_path=None, start_chapter_id=1):
    tu = (1, '32', 2.12)

    html_text = requests.get(book_root_url).text
    phrase_soup = BeautifulSoup(html_text, 'lxml')

    # fetch book meta data from info div
    book_meta_data = phrase_soup.find('div', id='info').h1.text.split(' / ')
    book_name = book_meta_data[0]
    book_author = book_meta_data[1]
    if save_path is None:
        save_path = book_name + ".txt"

    # find all chapters
    chapter_list_dl = phrase_soup.find('dl', class_='zjlist')

    curr_chapter_id = 0
    # use append mode to continue saving
    with open(save_path, "a") as save_file:
        for chapter_dd in chapter_list_dl.find_all('dd'):
            chapter_link = chapter_dd.a;
            if chapter_link is not None:
                # update current chapter id
                curr_chapter_id += 1
                if curr_chapter_id >= start_chapter_id:
                    # add relative url to the root url and phrase the html text
                    book_chapter_url = book_root_url + chapter_dd.a.get('href')
                    save_chapter(curr_chapter_id, book_chapter_url, book_name, chapter_link.text, save_file)


if __name__ == '__main__':
    fetch_book('https://www.bixiawenxue.org/book_57263/')
