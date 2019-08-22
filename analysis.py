from crawl import Crawler
from notifier.notifier import Notifier
import dbMysql
import dbClass
import env
import time


class Analyser:
    def __init__(self):
        self.crawler = Crawler()
        self.mysql_obj = dbMysql.DbMysql(env.DB_HOST, env.DB_PORT, env.DB_USERNAME, env.DB_PASSWORD, env.DB_DATABASE)
        self.db_obj = dbClass.DbWrapper(self.mysql_obj)

    def auth(self, api_key):
        # User-check with given API key.
        id_check = self.db_obj.get_data("api_key",
                                        COLUMNS="*",
                                        WHERE=[{'init': {'api_key': api_key}}],
                                        OPERATOR="eq")
        # Check if API key is valid.
        if id_check:
            user_id = id_check[0]['user_id']
            user_check = self.db_obj.get_data("user",
                                              COLUMNS=["id", "name_surname", "email"],
                                              WHERE=[{'init': {'id': user_id}}],
                                              OPERATOR="eq")
            # Check which user's key it is.
            if user_check:
                user_data = user_check[0]
                return {'user_id': user_id, 'name': user_data['name_surname'], 'email': user_data['email']}
            else:
                return False
        else:
            return False

    def analyse(self, url, user_data):
        if user_data is not False:
            user_id = user_data['user_id']
            user_name = user_data['name']
        else:
            return None, "Unauthorised!"

        # Proceed for website crawling.
        website_data = self.crawler.process_website(url)
        if website_data['status_code'] != 200:
            return None, "Non-OK HTTP response received!"

        meta_title = website_data['meta_title']
        meta_desc = website_data['meta_desc']
        h1 = website_data['h1']
        h2 = website_data['h2']

        # Add to analysed_url table of our database with the correct timestamp.
        checked_id = self.db_obj.exists('analysed_url', [('url', url)])
        if checked_id:  # It exists. Reset the error percentage for further analysis and update the time accessed to it.
            url_id = checked_id
            try:
                self.db_obj.update_data('analysed_url',
                                        [('time_accessed', time.time())],
                                        checked_id)
            except Exception as e:
                print(e)
                return None, "Action could not be performed. Query did not execute successfully."

            # Check for missing attributes. If problems are not noted before, add them.
            # Remove any problems that are solved.

            # Get the problems related to that url id.
            url_errors = [row['error_id'] for row in
                          self.db_obj.execute(
                              "SELECT error_id FROM analysis_errors WHERE url_id = " + str(checked_id))]

            # Title
            if meta_title is None and 2 not in url_errors:
                print("Title is missing and this was not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 2)],
                                        COLUMNS=['url_id', 'error_id'])
            elif meta_title is not None and 2 in url_errors:
                print("Title was missing but it seems to be fixed now.")
                try:
                    self.db_obj.execute(
                        "DELETE FROM analysis_errors "
                        "WHERE url_id = {0} AND error_id = {1} LIMIT 1".format(checked_id, 2))
                except Exception as e:
                    print(e)

            # Meta Desc
            if meta_desc is None and 1 not in url_errors:
                print("Desc is missing and this was not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 1)],
                                        COLUMNS=['url_id', 'error_id'])
            elif meta_desc is not None and 1 in url_errors:
                print("Desc was missing but it seems to be fixed now.")
                try:
                    self.db_obj.execute(
                        "DELETE FROM analysis_errors "
                        "WHERE url_id = {0} AND error_id = {1} LIMIT 1".format(checked_id, 1))
                except Exception as e:
                    print(e)

            # H1
            if h1 is None and 3 not in url_errors:
                print("H1 is missing and this was not noted before!")
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
                        "DELETE FROM analysis_errors "
                        "WHERE url_id = {0} AND error_id = {1} LIMIT 1".format(checked_id, 3))
                except Exception as e:
                    print(e)

            # H2
            if h2 is None and 4 not in url_errors:
                print("H2 is missing and this was not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 4)],
                                        COLUMNS=['url_id', 'error_id'])
            elif h2 is not None and 4 in url_errors:
                print("H2 was missing but it seems to be fixed now.")
                self.db_obj.execute(
                    "DELETE FROM analysis_errors "
                    "WHERE url_id = {0} AND error_id = {1} LIMIT 1".format(checked_id, 4))

            # Checking for duplicate meta data. Empty data doesn't count as a duplicate.
            dup_title = False if meta_title is None \
                else self.db_obj.exists('analysed_url', [('meta_title', meta_title)], exclude=('id', checked_id))

            dup_desc = False if meta_desc is None \
                else self.db_obj.exists('analysed_url', [('meta_desc', meta_desc)], exclude=('id', checked_id))

            dup_h1 = False if h1 is None \
                else self.db_obj.exists('analysed_url', [('h1', h1)], exclude=('id', checked_id))

            dup_h2 = False if h2 is None \
                else self.db_obj.exists('analysed_url', [('h2', h2)], exclude=('id', checked_id))

            # Warn if the error did not exist before or notify if the error is fixed this time.

            # Title
            if dup_title is not False and 5 not in url_errors:
                print("Title is duplicate and this was not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 5)],
                                        COLUMNS=['url_id', 'error_id'])
            elif dup_title is False and 5 in url_errors:
                print("Title was duplicate but it seems to be fixed now.")
                self.db_obj.execute(
                    "DELETE FROM analysis_errors "
                    "WHERE url_id = {0} AND error_id = {1} LIMIT 1".format(checked_id, 5))

            # Desc
            if dup_desc is not False and 6 not in url_errors:
                print("Desc is duplicate and this was not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 6)],
                                        COLUMNS=['url_id', 'error_id'])
            elif dup_desc is False and 6 in url_errors:
                print("Desc was duplicate but it seems to be fixed now.")
                self.db_obj.execute(
                    "DELETE FROM analysis_errors "
                    "WHERE url_id = {0} AND error_id = {1} LIMIT 1".format(checked_id, 6))

            # H1
            if dup_h1 is not False and 7 not in url_errors:
                print("H1 is duplicate and this was not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 7)],
                                        COLUMNS=['url_id', 'error_id'])
            elif dup_h1 is False and 7 in url_errors:
                print("H1 was duplicate but it seems to be fixed now.")
                self.db_obj.execute(
                    "DELETE FROM analysis_errors "
                    "WHERE url_id = {0} AND error_id = {1} LIMIT 1".format(checked_id, 7))

            # H2
            if dup_h2 is not False and 8 not in url_errors:
                print("H2 is duplicate and this was not noted before!")
                self.db_obj.insert_data('analysis_errors',
                                        [(checked_id, 8)],
                                        COLUMNS=['url_id', 'error_id'])
            elif dup_h2 is False and 8 in url_errors:
                print("H2 was duplicate but it seems to be fixed now.")
                self.db_obj.execute(
                    "DELETE FROM analysis_errors "
                    "WHERE url_id = {0} AND error_id = {1} LIMIT 1".format(checked_id, 8))

            # Update the crawled website info.
            self.db_obj.update_data('analysed_url', [
                ('meta_title', meta_title),
                ('meta_desc', meta_desc),
                ('h1', h1),
                ('h2', h2)
            ], checked_id)

        else:  # A unique record.
            try:
                self.db_obj.insert_data('analysed_url',
                                        [(url, time.time(), meta_title, meta_desc, h1, h2)],
                                        COLUMNS=['url', 'time_accessed', 'meta_title', 'meta_desc', 'h1', 'h2'])
                insert_id = self.db_obj.get_last_insert_id()
                url_id = insert_id

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

                # Checking for duplicate meta data. Empty data doesn't count as duplicate.
                dup_title = False if meta_title is None \
                    else self.db_obj.exists('analysed_url', [('meta_title', meta_title)], exclude=('id', insert_id))

                dup_desc = False if meta_desc is None \
                    else self.db_obj.exists('analysed_url', [('meta_desc', meta_desc)], exclude=('id', insert_id))

                dup_h1 = False if h1 is None \
                    else self.db_obj.exists('analysed_url', [('h1', h1)], exclude=('id', insert_id))

                dup_h2 = False if h2 is None \
                    else self.db_obj.exists('analysed_url', [('h2', h2)], exclude=('id', insert_id))

                # Warn if the error did not exist before or notify if the error is fixed this time.
                if dup_title is not False:
                    print("Title is duplicate!")
                    self.db_obj.insert_data('analysis_errors',
                                            [(insert_id, 5)],
                                            COLUMNS=['url_id', 'error_id'])
                if dup_desc is not False:
                    print("Desc is duplicate!")
                    self.db_obj.insert_data('analysis_errors',
                                            [(insert_id, 6)],
                                            COLUMNS=['url_id', 'error_id'])
                if dup_h1 is not False:
                    print("H1 is duplicate!")
                    self.db_obj.insert_data('analysis_errors',
                                            [(insert_id, 7)],
                                            COLUMNS=['url_id', 'error_id'])
                if dup_h2 is not False:
                    print("H2 is duplicate!")
                    self.db_obj.insert_data('analysis_errors',
                                            [(insert_id, 8)],
                                            COLUMNS=['url_id', 'error_id'])
            except Exception as e:
                print(e)
                return None, "Action could not be performed. Query did not execute successfully."

            try:
                # Update the crawled website info.
                self.db_obj.update_data('analysed_url', [
                    ('meta_title', meta_title),
                    ('meta_desc', meta_desc),
                    ('h1', h1),
                    ('h2', h2)
                ], checked_id)
            except Exception as e:
                print(e)
                return None, "Action could not be performed. Query did not execute successfully."

        # User's analysis was successful.
        try:
            self.db_obj.insert_data('analysis_user',
                                    [(url_id, user_id, time.time())],
                                    COLUMNS=['url_id', 'user_id', 'time'])
            print("Analysis request made by user #{0} ({1}) is successful!".format(user_id, user_name))

            try:
                # Get the issues for the last time.
                sql = """SELECT seo_errors.name, seo_errors.description
                FROM analysis_errors 
                JOIN analysed_url ON analysis_errors.url_id = analysed_url.id 
                JOIN seo_errors ON analysis_errors.error_id = seo_errors.id 
                WHERE analysed_url.id = {0}""".format(url_id)

                issues = self.db_obj.execute(sql)
                error_array = []
                for issue in issues:
                    error_array.append([issue['name'], issue['description']])

                # Fucking successful!
                return {url: error_array}

            except Exception as e:
                print(e)
                return None, "Issues could not be obtained."
        except Exception as e:
            print(e)
            return None, "Action could not be performed. Query did not execute successfully."

    def request_analysis(self, url, api_key, mode):
        auth = self.auth(api_key)
        if auth is False:
            return None, "Invalid API key."

        # Proceed as usual.
        user_data = auth
        user_name = auth['name']
        user_email = auth['email']

        # Obtained results from website(s) will be here.
        urls_error_list = []

        # Check the request mode.
        if mode != "batch":
            if isinstance(url, str):
                urls_error_list.append(self.analyse(url, user_data))
            else:
                return None, "Provided URL is not a string."
        else:
            # for API!
            for link in url:
                urls_error_list.append(self.analyse(link, user_data))

        try:
            # Notify the user about errors & fixes via email.
            notifier = Notifier()
            result = notifier.notify(user_email, user_name, urls_error_list)
        except Exception as e:
            print(e)
            return None, "Email could not be sent!"
        # End of the road.
        return result, "Success!"

    def main(self):
        print(self.request_analysis("http://127.0.0.1:5000/test-analysis",
                                    "7882e9e22bfa7dc96a6e8333a66091c51d5fe012",
                                    "batch"))


if __name__ == '__main__':
    a = Analyser()
    a.main()
