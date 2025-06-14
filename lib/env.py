from dotenv import load_dotenv
import os, datetime

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_USER_PWD = os.getenv("DB_USER_PWD")
DB_NAME = os.getenv("DB_NAME")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE = datetime.timedelta(minutes=60)
REFRESH_TOKEN_EXPIRE = datetime.timedelta(days=1)

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PWD = os.getenv("SMTP_PWD")