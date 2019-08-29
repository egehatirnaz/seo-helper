from crawl import Crawler
from notifier.notifier import Notifier
from urllib.parse import urljoin
import tldextract
import dbMysql
import dbClass
import env
import time
import requests
from multiprocessing.dummy import Pool


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

    @staticmethod
    def broken_link_helper(href):
        # Try out a HEAD request.
        try:
            r = requests.head(href, timeout=5)
            if not r.ok:
                # HEAD request failed, perhaps it is blocked? Try GET.
                r = requests.get(href, timeout=10)
                if not r.ok:
                    return False
        except requests.exceptions.Timeout:
            try:
                r = requests.get(href, timeout=10)
                if not r.ok:
                    return False
            except requests.exceptions.Timeout:
                return False
            except requests.exceptions.ConnectionError:
                return False
        except requests.exceptions.ConnectionError:
            try:
                r = requests.get(href, timeout=10)
                if not r.ok:
                    return False
            except requests.exceptions.Timeout:
                return False
            except requests.exceptions.ConnectionError:
                return False
        # Welcome to the internet where no URL behaves the same.
        return True

    @staticmethod
    def url_absolute(base_url, href_list):
        links = []
        for href in href_list:
            absolute_href = urljoin(base_url, href)
            if "http://" in absolute_href or "https://" in absolute_href:
                pure_href = absolute_href.split('#')[0].split('?')[0]
                if pure_href != base_url:
                    links.append(absolute_href)
        return links

    def find_broken_links(self, crawl_data, url):
        href_list = [tag['href'] for tag in crawl_data.find_all('a', href=True)]

        # Get absolute links from all ahref tags.
        absolute_links = self.url_absolute(url, href_list)

        # Send a head request to each and every one of them. Get boolean list of link being OK.
        thread_count = 100  # Parallel programming mf, ever heard of it?
        pool = Pool(thread_count)
        processed_links = pool.map(self.broken_link_helper, absolute_links)

        status_dict = list(zip(processed_links, absolute_links))
        filtered_links = [link[1] for link in status_dict if link[0] is False]

        return filtered_links

    def find_errors(self, defined_errors, crawl_data, url_id, dup_mode):
        url_error_list = []
        url_meta_list = []
        # Scan the metadata according to defined errors.

        for error in defined_errors:
            url_meta_content = None

            if error['attribute']:  # Compound metadata
                found_tag = crawl_data.find(error['tag'], attrs={error['attribute']: error['value']})

                # Are we checking for missing attribs?
                missing_mode = True if error['content'] is None else False

                if found_tag:
                    if found_tag['content']:
                        found_tag_content = found_tag['content']
                        if found_tag_content != "":  # Yeah it exists, but is it an empty string?
                            url_meta_content = found_tag_content
                            # Now we can check if we're analysing duplicates.
                            if not missing_mode:
                                # Check for duplicates.
                                # TODO: What a shit code this is. Take a look later on.
                                if dup_mode[0] is "default":
                                    dup_check = self.db_obj.exists('analysed_url_meta',
                                                                   [('tag', error['tag']),
                                                                    ('attribute', error['attribute']),
                                                                    ('value', error['value']),
                                                                    ('content', found_tag_content)],
                                                                   exclude=('url_id', url_id))
                                else:
                                    sql = """SELECT COUNT(*) AS count 
                                    FROM analysed_url_meta JOIN analysed_url
                                    on analysed_url_meta.url_id = analysed_url.id
                                    WHERE analysed_url.{0} = "{1}" 
                                    AND analysed_url_meta.tag = "{2}"
                                    AND analysed_url_meta.attribute = "{3}"
                                    AND analysed_url_meta.value = "{4}"
                                    AND analysed_url_meta.content = "{5}"
                                    AND analysed_url_meta.url_id != {6};""".format(
                                        dup_mode[0], dup_mode[1], error['tag'],
                                        error['attribute'], error['value'], found_tag_content, url_id)
                                    # Execute the query and find out if count > 0
                                    count = self.db_obj.execute(sql)[0]['count']
                                    if count <= 0:
                                        dup_check = False
                                    else:
                                        dup_check = True
                                if dup_check is not False:
                                    url_error_list.append(True)  # Duplicate!
                                else:
                                    url_error_list.append(False)  # Not duplicate!
                            else:
                                # Check for missing. But it is already non-empty.
                                url_error_list.append(False)
                        else:
                            # Tag content is empty.
                            if missing_mode:
                                # Check for missing. It is indeed empty.
                                url_error_list.append(True)
                            else:
                                # It is missing but we are checking for duplicates right now.
                                url_error_list.append(False)
                    else:
                        if missing_mode:
                            # The tag is missing. Put it in the errors.
                            url_error_list.append(True)
                        else:
                            # It is missing but we are checking for duplicates right now.
                            url_error_list.append(False)
                else:
                    # Tag is missing.
                    if missing_mode:
                        # The tag is missing. Put it in the errors.
                        url_error_list.append(True)
                    else:
                        # It is missing but we are checking for duplicates right now.
                        url_error_list.append(False)
            else:  # Simple tag checking
                found_tag = crawl_data.find(error['tag'])

                # Are we checking for missing attribs?
                missing_mode = True if error['content'] is None else False

                if found_tag:  # No need for checking duplication if it's already missing.
                    if found_tag.text:
                        found_tag_content = found_tag.text
                        url_meta_content = found_tag_content
                        # Now we can check if we're analysing duplicates.
                        if not missing_mode:
                            # Check for duplicates.
                            dup_check = self.db_obj.exists('analysed_url_meta', [('tag', error['tag']),
                                                                                 ('attribute', error['attribute']),
                                                                                 ('value', error['value']),
                                                                                 ('content', found_tag_content)],
                                                           exclude=('url_id', url_id))
                            # Warn if the error did not exist before or notify if the error is fixed this time.
                            if dup_check is not False:
                                # Duplicate!
                                url_error_list.append(True)
                            else:
                                # Not duplicate!
                                url_error_list.append(False)
                        else:
                            url_error_list.append(False)
                    else:
                        # Empty tag body?
                        if missing_mode:
                            # Check for missing. It is indeed empty.
                            url_error_list.append(True)
                        else:
                            # It is missing but we are checking for duplicates right now.
                            url_error_list.append(False)
                else:
                    # Tag is missing.
                    if missing_mode:
                        # The tag is missing. Put it in the errors.
                        url_error_list.append(True)
                    else:
                        # It is missing but we are checking for duplicates right now.
                        url_error_list.append(False)
            # Get the single metadata
            if error['content'] is not None:  # TODO: This shit needs to be addressed. There must be a better solution.
                url_meta_list.append({'tag': error['tag'],
                                      'attribute': error['attribute'],
                                      'value': error['value'],
                                      'content': url_meta_content})

        result = list(zip(list(x['id'] for x in defined_errors), url_error_list))
        return result, url_meta_list

    def analyse(self, url, user_data, **kwargs):
        if user_data is not False:
            user_id = user_data['user_id']
            user_name = user_data['name']
        else:
            return None, "Unauthorised!"

        # Proceed for website crawling.
        website_data = self.crawler.get_crawled(url)
        if website_data['status_code'] != 200:
            return None, "Non-OK HTTP response received!"

        # Handle the URL changes for 301, 302, etc.
        url = website_data['url']

        # Get the domain and/or subdomain of this URL.
        extracted_url = tldextract.extract(url)
        subdomain = extracted_url.subdomain
        domain = extracted_url.domain

        # Obtain crawl data for website.
        crawl = website_data['content']

        # Check which mode are we in for checking duplicate contents.
        dup_mode = ["default", None]
        if 'mode' in kwargs:
            if kwargs['mode'] == 'domain':
                dup_mode = ["domain", domain]
            elif kwargs['mode'] == 'subdomain':
                dup_mode = ["subdomain", subdomain]

        # Check broken references in this website.
        broken_links = self.find_broken_links(crawl, url)

        # Add to analysed_url table of our database with the correct timestamp.
        checked_id = self.db_obj.exists('analysed_url', [('url', url)])
        if checked_id:  # It exists. Update the time accessed to it.
            url_id = checked_id

            # Update the time of this url.
            try:
                self.db_obj.update_data('analysed_url',
                                        [('time_accessed', time.time())],
                                        checked_id)
            except Exception as e:
                print(e)
                return None, "Action could not be performed. Query did not execute successfully."

            # Get ALL defined SEO Errors. (So that you can check it during analysis.)
            defined_errors = self.db_obj.execute("SELECT * FROM seo_errors")

            # Get the found error list of this URL.
            errors = self.find_errors(defined_errors, crawl, url_id, dup_mode)
            error_list = errors[0]
            meta_list = errors[1]

            # Get the previously existing problems related to that url id.
            previous_url_errors = [row['error_id'] for row in
                                   self.db_obj.execute(
                                       "SELECT error_id FROM analysis_errors WHERE url_id = " + str(checked_id))]

            # Clear out the existing metadata. (I'm not content with this solution. I should've left the unchanged data)
            self.db_obj.execute("DELETE FROM analysed_url_meta WHERE url_id = " + str(url_id))

            # Add the meta data to DB.
            for meta in meta_list:
                self.db_obj.insert_data('analysed_url_meta',
                                        [(url_id, meta['tag'], meta['attribute'], meta['value'], meta['content'])],
                                        COLUMNS=['url_id', 'tag', 'attribute', 'value', 'content'])

            # Iterate the error list
            for error in error_list:
                if error[0] in previous_url_errors and error[1] is False:
                    # Delete the fixed errors.
                    print("Error with id ", error[0], " is fixed now!")
                    self.db_obj.execute(
                        "DELETE FROM analysis_errors "
                        "WHERE url_id = {0} AND error_id = {1} LIMIT 1".format(checked_id, error[0]))
                elif error[0] not in previous_url_errors and error[1] is True:
                    # Add the previously non-existing errors.
                    print("A wild error with id ", error[0], " has just appeared!")  # Pokemon?
                    self.db_obj.insert_data('analysis_errors',
                                            [(url_id, error[0])],
                                            COLUMNS=['url_id', 'error_id'])
        else:  # A unique record.
            try:
                # Add the new site to analysed_url.
                self.db_obj.insert_data('analysed_url',
                                        [(url, subdomain, domain, time.time())],
                                        COLUMNS=['url', 'subdomain', 'domain', 'time_accessed'])
                insert_id = self.db_obj.get_last_insert_id()
                url_id = insert_id

                # Get ALL defined SEO Errors. (So that you can check it during analysis.)
                defined_errors = self.db_obj.execute("SELECT * FROM seo_errors")

                # Get the found error list of this URL.
                errors = self.find_errors(defined_errors, crawl, url_id, dup_mode)
                error_list = errors[0]
                meta_list = errors[1]

                # Add the meta data to DB.
                for meta in meta_list:
                    self.db_obj.insert_data('analysed_url_meta',
                                            [(url_id, meta['tag'], meta['attribute'], meta['value'], meta['content'])],
                                            COLUMNS=['url_id', 'tag', 'attribute', 'value', 'content'])

                # Iterate the error list
                for error in error_list:
                    if error[1] is True:
                        # Add the newly found error.
                        print("A wild error with id ", error[0], " has just appeared!")  # Pokemon?
                        self.db_obj.insert_data('analysis_errors',
                                                [(url_id, error[0])],
                                                COLUMNS=['url_id', 'error_id'])

            except Exception as e:
                print(e)
                return None, "Action could not be performed. Query did not execute successfully."

        try:
            # Clear out the existing broken links.
            # (I'm not content with this solution. Maybe I should've left the unchanged data)
            self.db_obj.execute("DELETE FROM analysed_url_href_404 WHERE `url_id` = " + str(url_id))

            if len(broken_links) > 0:
                # Add the broken links to DB.
                for link in broken_links:
                    self.db_obj.insert_data('analysed_url_href_404',
                                            [(url_id, link)],
                                            COLUMNS=['url_id', 'href'])
        except Exception as e:
            print(e)
            return None, "Action could not be performed. Query did not execute successfully."

        # User's analysis was successful.
        try:
            # Check if this analysis was done before.
            checked_url_id = self.db_obj.exists('analysis_user', [('url_id', url_id), ('user_id', user_id)])
            if checked_url_id:  # It exists. Update the time accessed to it.
                self.db_obj.execute("UPDATE analysis_user SET time = {0} WHERE user_id = {1} AND url_id = {2}"
                                    .format(time.time(), user_id, url_id))
            else:
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
                for link in broken_links:
                    error_array.append(["Referencing Broken / Dead URL",
                                        "The following referenced URL is returning a 4xx/5xx response: " + link])
                # Fucking successful!
                return {url: error_array}, "Success!"

            except Exception as e:
                print(e)
                return None, "Issues could not be obtained."
        except Exception as e:
            print(e)
            return None, "Action could not be performed. Query did not execute successfully."

    def request_analysis(self, url, api_key, mode, **kwargs):
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
                if 'dup_mode' in kwargs:
                    if kwargs['dup_mode'] == 'domain':
                        urls_error_list.append(self.analyse(url, user_data, mode='domain')[0])
                    elif kwargs['dup_mode'] == 'subdomain':
                        urls_error_list.append(self.analyse(url, user_data, mode='subdomain')[0])
                else:
                    urls_error_list.append(self.analyse(url, user_data)[0])
            else:
                return None, "Provided URL is not a string."
        else:
            # for API!
            if 'dup_mode' in kwargs:
                if kwargs['dup_mode'] == 'domain':
                    for link in url:
                        urls_error_list.append(self.analyse(link, user_data, mode='domain')[0])
                elif kwargs['dup_mode'] == 'subdomain':
                    for link in url:
                        urls_error_list.append(self.analyse(link, user_data, mode='subdomain')[0])
            else:
                for link in url:
                    urls_error_list.append(self.analyse(link, user_data)[0])
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
        mode = 'subdomain'
        print(self.request_analysis(["https://developers.jotform.com"],
                                    "7882e9e22bfa7dc96a6e8333a66091c51d5fe012", "batch", dup_mode=mode))


if __name__ == '__main__':
    a = Analyser()
    a.main()
