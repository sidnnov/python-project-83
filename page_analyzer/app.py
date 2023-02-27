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
import psycopg2.extras
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


def is_there(name: str) -> int:
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute("SELECT * FROM urls WHERE name = %s", (name,))
            data = curs.fetchall()
    if data:
        return data[0][0]
    return 0


@app.route("/")
def index():
    return render_template("/index.html")


@app.route("/urls", methods=["POST"])
def add_url():
    url_with_form = request.form["url"]
    if not url(url_with_form):
        flash("Некорректный URL", "danger")
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            "/index.html",
            url=url_with_form,
            messages=messages,
        ), 422
    correct_url = normalize_url(url_with_form)
    id = is_there(correct_url)
    if id:
        flash("Страница уже существует", "info")
        return redirect(url_for("get_url", id=id))
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as curs:
            curs.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id",
                # (correct_url, datetime.now().date())
                (correct_url, datetime.now().isoformat(timespec="seconds")),
            )
            data = curs.fetchone()
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("get_url", id=data.id))


@app.route("/urls", methods=["GET"])
def get_urls():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as curs:
            curs.execute("SELECT * FROM urls ORDER BY id DESC")
            data = curs.fetchall()
    return render_template("urls.html", data=data)


@app.route("/urls/<id>")
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as curs:
            curs.execute("SELECT * FROM urls WHERE id = %s", (id,))
            urls_data = curs.fetchone()
            curs.execute("SELECT * FROM url_checks WHERE url_id = %s", (urls_data.id,))
            checks_data = curs.fetchall()
    if not urls_data:
        return render_template('404.html')
    return render_template(
        "url.html",
        urls_id=urls_data.id,
        name=urls_data.name,
        urls_date=urls_data.created_at,
        checks_data=checks_data,
        messages=messages,
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.route("/urls/<id>/checks", methods=["POST", "GET"])
def check_url(id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as curs:
            curs.execute(
                "INSERT INTO url_checks (url_id, created_at) VALUES (%s, %s)",
                # (correct_url, datetime.now().date())
                (id, datetime.today().isoformat(),),
            )
    flash("Страница успешно проверена", "success")
    return redirect(url_for('get_url', id=id))
