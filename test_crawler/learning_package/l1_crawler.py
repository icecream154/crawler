from bs4 import BeautifulSoup

if __name__ == '__main__':

    temp_list = []
    temp_list[9] = 'hello'
    print(temp_list[9])

    with open('jammy.html', 'r') as jammy_html:
        content = jammy_html.read()
        # print(content)
        soup = BeautifulSoup(content, 'lxml')
        # h5_tags = soup.find_all('h5')
        # for h5_tag in h5_tags:
        #     print(h5_tag.text)

        block_divs = soup.find_all('div', class_='block')
        for block_div in block_divs:
            for h5_tag in block_div.find_all('h5'):
                print(h5_tag.text)
