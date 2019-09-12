###### This project is a work in progress!

# SEO Helper
This project helps the process of analyzing a website for common SEO mistakes and errors. A URL given as a parameter will be crawled and analyzed for certain missing HTML meta tags. Analysis requests will be made through an API with a user's API key. The user will also be notified about existing SEO related errors.

## What does it do?
SEO Helper is an analysis tool.

For each provided URL, we check for common SEO bad practices regarding the metadata of the website.
Each provided URL will be scanned for certain missing or duplicate HTML meta tags.
We also check for broken links referenced in this URL.

If certain errors are encountered in your URL, you will be notified via e-mail.

## How to use?
After you sign up to SEO Helper with your e-mail address, an API key will be connected to that e-mail address.
With this key, you will be able to use SEO Helper to analyse any given URL.

## API Documentation
[Click here](https://documenter.getpostman.com/view/5446795/SVmqzfkv?version=latest) to check out the API documentation. This API documentation is based on the Postman Collection for SEO Helper. SEO Helper web-service uses these API endpoints for the requests made via AJAX.

## Getting Started
### Dependencies
The necessary Python packages are listed under requirements.txt. You can run ```pip install -r requirements.txt``` to install the required packages.

### MySQL Database
A MySQL database is required to be up and running. After setting up your database, you must create the tables needed by SEO Helper by importing the SQL (`database.sql`) found inside the project root folder. 

After the database is ready, proceed to the next step and state the DB information as environment variable.

### Environment Variables
A custom created `env.py` file placed inside project's root directory will contain the necessary environment variables. These variables are:
```
DB_HOST = "..."             # Host address of your database.
DB_PORT = "..."             # Port of your database.
DB_USERNAME = "..."         # User of the database.
DB_PASSWORD = "..."         # Password of the database user.
DB_DATABASE = "seo-helper"  # Do not change.

# Auth Key that is used to validate the API requests.
# I recommend having a randomized value.
# EVERY request to API needs to have a header value that matches this value.
AUTH_KEY = "..."

SMTP_PORT = ""          # Port for the preferred SMTP service.
SMTP_EMAIL = ""         # E-mail of the sender account.
SMTP_PASSWORD = ""      # Password of the sender account. For security reasons, please choose an application based account password.
SMTP_SERVER = ""        # Your preferred SMTP server.
```

### Good to go! Let's review.
By this point...
- You should have the project dependencies installed.
- Your database should be ready and initialized.
- env.py is created inside the project root folder and is filled with the required variables.

You are now ready to run `app.py`. After running it, Flask will print an output stating where the files are hosted. (i.e: Base URL.)
API endpoints are under "`BASE_URL`/api". You can check the API documentation for further information.

That's it. Thank you for your time!

You can contact me from [egehatirnaz@gmail.com](mailto:egehatirnaz@gmail.com).
