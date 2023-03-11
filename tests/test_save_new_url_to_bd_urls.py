from page_analyzer.app import save_new_url_to_bd_urls
from psycopg2.extras import NamedTupleCursor
import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
URL = "http://google.com"


def clear_bd():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute("""DROP TABLE IF EXISTS url_checks""")
            curs.execute("""DROP TABLE IF EXISTS urls""")
            curs.execute("""
                CREATE TABLE urls (
                    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    name varchar(255),
                    created_at timestamp)""")
            curs.execute("""
                CREATE TABLE url_checks (
                    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    url_id bigint REFERENCES urls(id),
                    status_code integer,
                    h1 varchar(255),
                    title varchar(255),
                    description text,
                    created_at date)""")


def save_url():
    clear_bd()
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('''
                INSERT INTO urls (name)
                VALUES (%s) RETURNING id''', (
                URL,),
            )
            data = curs.fetchone()
    return data.id


def test_save_new_url_to_bd_urls_true():
    clear_bd()
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            id, result = save_new_url_to_bd_urls(URL)
            curs.execute('''
                SELECT id FROM urls WHERE name = %s''', (URL,))
            data = curs.fetchone()
    clear_bd()
    assert (data.id, True) == (id, result)


def test_save_new_url_to_bd_urls_false():
    clear_bd()
    data_id = save_url()
    id, result = save_new_url_to_bd_urls(URL)
    clear_bd()
    assert (data_id, False) == (id, result)
