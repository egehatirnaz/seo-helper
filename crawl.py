from bs4 import BeautifulSoup
import requests


class Crawler:
    def get_crawled(self, source_url):
        try:
            r = requests.get(source_url)
            source = BeautifulSoup(r.content, "html5lib")
            return source
        except Exception:
            return None

    def process_website(self, source_url):
        soup = self.get_crawled(source_url)
        if soup:
            found_meta_title = soup.find('title')
            found_meta_desc = soup.find('meta', attrs={"name": "description"})['content']
            found_h1 = soup.find('h1')
            found_h2 = soup.find('h2')

            meta_title = found_meta_title.string if found_meta_title else None
            meta_desc = found_meta_desc if found_meta_desc else None
            h1 = found_h1.string if found_h1 else None
            h2 = found_h2.string if found_h2 else None

            return {
                "source_url": source_url,
                "meta_title": meta_title,
                "meta_desc": meta_desc,
                "h1": h1,
                "h2": h2
            }
        else:
            return None

    def main(self):
        print(self.process_website("https://www.jasflkjaslfkjaslfkjasfklkasşkfas.com"))
        print(self.process_website("https://www.jotform.com/blog"))


if __name__ == '__main__':
    c = Crawler()
    c.main()
