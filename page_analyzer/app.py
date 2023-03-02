from flask import (
    Flask,
    render_template,
    request,
    flash,
    get_flashed_messages,
    url_for,
    redirect,
)
from dotenv import load_dotenv
from validators import url
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup
from psycopg2.extras import NamedTupleCursor
import psycopg2
import requests
import os


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")


def normalize_url(url: str) -> str:
    url_parse = urlparse(url)
    correct_url = url_parse._replace(
        path="", params="", query="", fragment="").geturl()
    return correct_url


def is_duplicate_url(name: str) -> int:
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('''
            SELECT id FROM urls WHERE name = %s''', (name,))
            data = curs.fetchone()
    return data.id if data else None


def get_content(data):
    content = BeautifulSoup(data.text, 'lxml')
    h1 = content.find('h1')
    title = content.find('title')
    meta_data = content.find('meta', attrs={'name': 'description'})
    h1 = h1.text if h1 else ''
    title = title.text if title else ''
    description = meta_data.get('content') if meta_data else ''
    return h1, title, description


def save_new_url_to_bd_urls(url: str) -> int:
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('''
            INSERT INTO urls (name, created_at)
            VALUES (%s, %s) RETURNING id''', (
                url, datetime.now().isoformat(timespec="seconds")),
            )
            data = curs.fetchone()
    return data.id


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.route("/")
def index():
    return render_template("/index.html")


@app.route("/urls", methods=["POST"])
def add_url():
    url_with_form = request.form["url"]
    if not url(url_with_form):
        if len(url_with_form) > 255:
            flash("URL превышает 255 символов", "danger")
        flash("Некорректный URL", "danger")
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            "/index.html",
            url=url_with_form,
            messages=messages), 422
    if len(url_with_form) > 255:
        flash("URL превышает 255 символов", "danger")
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            "/index.html",
            url=url_with_form,
            messages=messages), 422
    correct_url = normalize_url(url_with_form)
    id = is_duplicate_url(correct_url)
    if id:
        flash("Страница уже существует", "info")
        return redirect(url_for("get_url", id=id))
    new_id = save_new_url_to_bd_urls(correct_url)
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("get_url", id=new_id))


@app.route("/urls", methods=["GET"])
def get_urls():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('''
            SELECT DISTINCT ON (urls.id, urls.name) urls.id, urls.name,
                url_checks.created_at, url_checks.status_code
            FROM urls LEFT JOIN url_checks ON urls.id = url_checks.url_id
            ORDER BY urls.id DESC''')
            data = curs.fetchall()
    return render_template("urls.html", data=data)


@app.route("/urls/<id>", methods=["GET"])
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            try:
                curs.execute('''
                SELECT * FROM urls WHERE id = %s''', (id,))
            except psycopg2.errors.InvalidTextRepresentation:
                return render_template('404.html')
            urls_data = curs.fetchone()
            if not urls_data:
                return render_template('404.html')
            curs.execute('''
            SELECT * FROM url_checks
            WHERE url_id = %s ORDER BY id DESC''', (urls_data.id,))
            checks_data = curs.fetchall()
    return render_template(
        "url.html",
        urls_id=urls_data.id,
        name=urls_data.name,
        urls_date=urls_data.created_at,
        checks_data=checks_data,
        messages=messages,
    )


@app.route("/urls/<id>/checks", methods=["POST", "GET"])
def check_url(id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('''
            SELECT name from urls WHERE id = %s''', (id,))
            data = curs.fetchone()
    try:
        response = requests.get(data.name)
        h1, title, description = get_content(response)
    except requests.exceptions.ConnectionError:
        flash("Произошла ошибка при проверке", "danger")
        return redirect(url_for('get_url', id=id))
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('''
            INSERT INTO url_checks
            (url_id, created_at, status_code, h1, title, description)
            VALUES (%s, %s, %s, %s, %s, %s)''', (
                id, datetime.today().isoformat(),
                response.status_code, h1, title, description),
            )
    flash("Страница успешно проверена", "success")
    return redirect(url_for('get_url', id=id))
