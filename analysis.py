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

            # Get the problems related to that url id.
            url_errors = [row['error_id'] for row in
                          self.db_obj.execute("SELECT error_id FROM analysis_errors WHERE url_id = " + str(checked_id))]
            print(url_errors)

            # Title
            if meta_title is None and 2 not in url_errors:
                print("Title is missing and this is not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 2)],
                                        COLUMNS=['url_id', 'error_id'])
            elif meta_title is not None and 2 in url_errors:
                print("Title was missing but it seems to be fixed now.")
                try:
                    self.db_obj.execute(
                        "DELETE FROM analysis_errors WHERE url_id = {0} AND error_id = {1} LIMIT 1"
                            .format(checked_id, 2))
                except Exception as e:
                    print(e)

            # Meta Desc
            if meta_desc is None and 1 not in url_errors:
                print("Desc is missing and this is not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 1)],
                                        COLUMNS=['url_id', 'error_id'])
            elif meta_desc is not None and 1 in url_errors:
                print("Desc was missing but it seems to be fixed now.")
                try:
                    self.db_obj.execute(
                        "DELETE FROM analysis_errors WHERE url_id = {0} AND error_id = {1} LIMIT 1"
                            .format(checked_id, 1))
                except Exception as e:
                    print(e)

            # H1
            if h1 is None and 3 not in url_errors:
                print("H1 is missing and this is not noted before!")
                try:
                    self.db_obj.insert_data('analysis_errors',
                                            [(checked_id, 3)],
                                            COLUMNS=['url_id', 'error_id'])
                except Exception as e:
                    print(e)
            elif h1 is not None and 3 in url_errors:
                print("H1 was missing but it seems to be fixed now.")
                try:
                    self.db_obj.execute(
                        "DELETE FROM analysis_errors WHERE url_id = {0} AND error_id = {1} LIMIT 1".format(checked_id,
                                                                                                           3))
                except Exception as e:
                    print(e)

            # H2
            if h2 is None and 4 not in url_errors:
                print("H2 is missing and this is not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 4)],
                                        COLUMNS=['url_id', 'error_id'])
            elif h2 is not None and 4 in url_errors:
                print("H2 was missing but it seems to be fixed now.")
                self.db_obj.execute(
                    "DELETE FROM analysis_errors WHERE url_id = {0} AND error_id = {1} LIMIT 1".format(checked_id, 4))

            # TODO: Check for duplicate attributes.

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
                if meta_title is None:
                    print("Title is not found!")
                    self.db_obj.insert_data('analysis_errors',
                                            [(insert_id, 2)],
                                            COLUMNS=['url_id', 'error_id'])

                if meta_desc is None:
                    print("Meta Desc is not found!")
                    self.db_obj.insert_data('analysis_errors',
                                            [(insert_id, 1)],
                                            COLUMNS=['url_id', 'error_id'])

                if h1 is None:
                    print("H1 is not found!")
                    self.db_obj.insert_data('analysis_errors',
                                            [(insert_id, 3)],
                                            COLUMNS=['url_id', 'error_id'])

                if h2 is None:
                    print("H2 is not found!")
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
        self.analyse("https://www.jotform.com/theme-store/collection/3d")


if __name__ == '__main__':
    a = Analyser()
    a.main()
