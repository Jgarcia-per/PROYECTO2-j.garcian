import os

class Config:
    MYSQL_DATABASE_USER = 'root'
    MYSQL_DATABASE_PASSWORD = '1027150930Juan*'
    MYSQL_DATABASE_DB = 'heladeria'
    MYSQL_DATABASE_HOST = 'localhost'
    SECRET_KEY = os.urandom(24)
