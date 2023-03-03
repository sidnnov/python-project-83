from page_analyzer.app import is_duplicate_url
import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def test_is_dublicate_url():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute('''DELETE from url_checks''')
            curs.execute('''DELETE from urls''')
            curs.execute('''
            INSERT INTO urls (name)
            VALUES (%s) RETURNING id''', ('http://google.com',))
            id = curs.fetchone()[0]
    assert is_duplicate_url('http://google.com') == id
    assert is_duplicate_url('http://mail.ru') is None
