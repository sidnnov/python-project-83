from page_analyzer.app import save_new_url_to_bd_urls
import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def test_save_new_url_to_bd_urls():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute("""DELETE from url_checks""")
            curs.execute("""DELETE from urls""")
            id = save_new_url_to_bd_urls("http://google.com")
            curs.execute(
                """
                SELECT id, name FROM urls WHERE name = %s""",
                ("http://google.com",),
            )
            id_urls, _ = curs.fetchone()
    assert id_urls == id
