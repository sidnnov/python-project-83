from page_analyzer.app import normalize_url
import pytest


@pytest.mark.parametrize(
    "url, result",
    [
        (
            "http://docs.python.org:80/3/library/urllib.parse.html",
            "http://docs.python.org:80",
        ),
        (
            "https://ru.hexlet.io/programs/python",
            "https://ru.hexlet.io",
        ),
        (
            "", "",
        )
    ],
)
def test_normalize_url(url, result):
    assert normalize_url(url) == result
