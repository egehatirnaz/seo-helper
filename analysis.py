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

        checked_id = self.db_obj.exists('analysed_url', [('url', url)])
        if checked_id:  # It exists. Reset the error percentage for further analysis and update the time accessed to it.
            try:
                self.db_obj.update_data('analysed_url',
                                        [('error_percentage', 0.00), ('time_accessed', time.time())],
                                        checked_id)
            except Exception as e:
                print(e)
                return None, "Action could not be performed. Query did not execute successfully."

            # Check for missing attributes. If problems are not noted before, add them.
            # Remove any problems that are solved.

            # Spotted problems that are not noted before:
            if meta_title is None and not self.db_obj.exists(
                        'analysis_errors', [('url_id', checked_id), ('error_id', 2)]):
                print("Title is missing and this is not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 2)],
                                        COLUMNS=['url_id', 'error_id'])

            if meta_desc is None and not self.db_obj.exists(
                        'analysis_errors', [('url_id', checked_id), ('error_id', 1)]):
                print("Desc is missing and this is not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 1)],
                                        COLUMNS=['url_id', 'error_id'])

            if h1 is None and not self.db_obj.exists(
                        'analysis_errors', [('url_id', checked_id), ('error_id', 3)]):
                print("H1 is missing and this is not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 3)],
                                        COLUMNS=['url_id', 'error_id'])

            if h2 is None and not self.db_obj.exists(
                        'analysis_errors', [('url_id', checked_id), ('error_id', 4)]):
                print("H2 is missing and this is not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 4)],
                                        COLUMNS=['url_id', 'error_id'])

            # Check for duplicate attributes.

            # Update the crawled website info.
            self.db_obj.update_data('websites', [
                                        ('meta_title', meta_title),
                                        ('meta_desc', meta_desc),
                                        ('h1', h1),
                                        ('h2', h2)
                                    ], checked_id)

        else:  # A unique record.
            try:
                self.db_obj.insert_data('analysed_url',
                                        [(url, time.time())],
                                        COLUMNS=['url', 'time_accessed'])
                insert_id = self.db_obj.get_last_insert_id()

                # Check for missing attributes.
                if meta_title is None and not self.db_obj.exists(
                        'analysis_errors', [('url_id', insert_id), ('error_id', 2)]):
                    self.db_obj.insert_data('analysis_errors',
                                            [(insert_id, 2)],
                                            COLUMNS=['url_id', 'error_id'])

                if meta_desc is None and not self.db_obj.exists(
                        'analysis_errors', [('url_id', insert_id), ('error_id', 1)]):
                    self.db_obj.insert_data('analysis_errors',
                                            [(insert_id, 1)],
                                            COLUMNS=['url_id', 'error_id'])

                if h1 is None and not self.db_obj.exists(
                        'analysis_errors', [('url_id', insert_id), ('error_id', 3)]):
                    self.db_obj.insert_data('analysis_errors',
                                            [(insert_id, 3)],
                                            COLUMNS=['url_id', 'error_id'])

                if h2 is None and not self.db_obj.exists(
                        'analysis_errors', [('url_id', insert_id), ('error_id', 4)]):
                    self.db_obj.insert_data('analysis_errors',
                                            [(insert_id, 4)],
                                            COLUMNS=['url_id', 'error_id'])

                # TODO: Check for duplicate attributes.

            except Exception as e:
                print(e)
                return None, "Action could not be performed. Query did not execute successfully."

            # Add the crawled website
            self.db_obj.insert_data('websites',
                                    [(insert_id, meta_title, meta_desc, h1, h2)],
                                    COLUMNS=['url_id', 'meta_title', 'meta_desc', 'h1', 'h2'])

    def main(self):
        self.analyse("https://www.icerik.com/urunler/test2")


if __name__ == '__main__':
    a = Analyser()
    a.main()
