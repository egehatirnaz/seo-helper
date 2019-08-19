from crawl import Crawler
import dbMysql
import dbClass
import env
import time


class Analyser:
    def __init__(self):
        self.crawler = Crawler()
        self.mysql_obj = dbMysql.DbMysql(env.DB_HOST, env.DB_PORT, env.DB_USERNAME, env.DB_PASSWORD, env.DB_DATABASE)
        self.db_obj = dbClass.DbWrapper(self.mysql_obj)

    def analyse(self, url):
        website_data = self.crawler.process_website(url)

        meta_title = website_data['meta_title']
        meta_desc = website_data['meta_desc']
        h1 = website_data['h1']
        h2 = website_data['h2']

        # TODO: What if the crawled page is actually a non-200 page? 400, 404, etc.

        # Add to analysed_url table of our database with the correct timestamp.

        checked_id = self.db_obj.exists('analysed_url', 'url', url)
        if checked_id:
            # It exists. Reset the error percentage for further analysis and update the time accessed to it.
            try:
                self.db_obj.update_data('analysed_url',
                                        [('error_percentage', 0.00), ('time_accessed', time.time())],
                                        checked_id)
            except Exception as e:
                print(e)
                return None, "Action could not be performed. Query did not execute successfully."

            # Check for missing attributes.
            if meta_title is None:
                print("Title is missing!")
            if meta_desc is None:
                print("Desc is missing!")
            if h1 is None:
                print("H1 is missing!")
            if h2 is None:
                print("H2 is missing!")

            # Check for duplicate attributes.

        else:
            try:
                self.db_obj.insert_data('analysed_url',
                                        [(url, time.time())],
                                        COLUMNS=['url', 'time_accessed'])
            except Exception as e:
                print(e)
                return None, "Action could not be performed. Query did not execute successfully."

            # Check for missing attributes.
            if meta_title is None:
                print("Title is missing!")
            if meta_desc is None:
                print("Desc is missing!")
            if h1 is None:
                print("H1 is missing!")
            if h2 is None:
                print("H2 is missing!")

            # Check for duplicate attributes.

    def main(self):
        self.analyse("https://www.icerik.com/urunler/")


if __name__ == '__main__':
    a = Analyser()
    a.main()
