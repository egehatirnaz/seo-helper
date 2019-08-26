from bs4 import BeautifulSoup
import requests


class Crawler:
    @staticmethod
    def get_crawled(source_url):
        try:
            r = requests.get(source_url)
            status_code = r.status_code
            source = None
            if status_code == 200:
                source = BeautifulSoup(r.content, "html5lib")
            return {'status_code': status_code, 'url': r.url, 'content': source}
        except Exception as e:
            print(e)
            return None

    # We shall not use this one.
    def process_website(self, source_url):
        response = self.get_crawled(source_url)
        status_code = response['status_code']
        soup = response['content']
        if soup and status_code == 200:
            found_meta_title = soup.find('title')
            possible_desc = soup.find('meta', attrs={"name": "description"})
            if possible_desc:
                found_meta_desc = possible_desc['content']
            else:
                found_meta_desc = None
            found_h1 = soup.find('h1')
            found_h2 = soup.find('h2')

            meta_title = found_meta_title.string if found_meta_title else None
            meta_desc = found_meta_desc if found_meta_desc else None
            h1 = found_h1.string if found_h1 else None
            h2 = found_h2.string if found_h2 else None

            return {
                "status_code": status_code,
                "source_url": source_url,
                "meta_title": meta_title,
                "meta_desc": meta_desc,
                "h1": h1,
                "h2": h2
            }
        else:
            return {
                "status_code": status_code,
                "source_url": None,  # This will create a trouble later on, I'm sure of it.
                "meta_title": None,
                "meta_desc": None,
                "h1": None,
                "h2": None
            }

    def main(self):
        # print(self.get_crawled("https://www.jasflkjaslfkjaslfkjasfklkasşkfas.com"))
        print(self.get_crawled("http://127.0.0.1:5000/test-301"))


if __name__ == '__main__':
    c = Crawler()
    c.main()
