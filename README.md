###### This project is a work in progress!

# SEO Helper
This project helps the process of analyzing a website for common SEO mistakes and errors. A URL given as a parameter will be crawled and analyzed for certain missing HTML meta tags. Analysis requests will be made through an API with a user's API key. The user will also be notified about existing SEO related errors.

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
```

