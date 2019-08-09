from bs4 import BeautifulSoup
import requests


class Crawler:
    def __init__(self):
        self.ignore = '\"', '“', '”', '\'', '’', '- ', ':', ',', ';', '.'

    def get_crawled(self, source_url):
        r = requests.get(source_url)
        source = BeautifulSoup(r.content, "html5lib")
        return source

    # We're all perverts here.
    def get_head(self, crawl):
        return crawl.head

    def main(self):
        soup = self.get_crawled("https://www.icerik.com/blog")
        meta_tag = soup.find('meta', attrs={"name": "description"})
        print(meta_tag)


if __name__ == '__main__':
    c = Crawler()
    c.main()
