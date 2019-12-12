import os
from dotenv import load_dotenv
load_dotenv()


## Flask Settings
SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

# DB settings
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DATABASE")
MYSQL_CURSORCLASS = "DictCursor"
default_authentication_plugin = "sha2_password"
