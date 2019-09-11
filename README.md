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
The necessary Python packages are listed under requirements.txt. You can run ```pip install -r requirements.txt``` to install the required packages.

A custom created `env.py` file placed inside project's root directory will contain the necessary environment variables. These variables are:
```
DB_HOST = *Host address of your database*
DB_PORT = *Port of your database*
DB_USERNAME = *User of the database*
DB_PASSWORD = *Password of the database user*
DB_DATABASE = "seo-helper"

AUTH_KEY = "..." *A predetermined authorization key for admin*

SMTP_PORT = *Port for the preferred SMTP service.*
SMTP_EMAIL = *E-mail of the sender account*
SMTP_PASSWORD = *Password of the sender account*
SMTP_SERVER = *Your preferred SMTP server*
```

After setting up env.py and getting the required packages, you're able to run `app.py` and connection to your MySQL database will be established. `http://localhost:5000` will serve your files.
