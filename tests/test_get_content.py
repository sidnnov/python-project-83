from page_analyzer.app import get_content
import pytest

META1 = """
<html>
    <head>
        <h1>h1</h1>
        <title>title</title>
        <meta name="description" content="description">
    </head>
</html>"""
META2 = """
<html>
    <head>
        <title>title</title>
        <meta name="description" content="description">
    </head>
</html>"""
META3 = """
<html>
    <head>
        <h1>h1</h1>
        <meta name="description" content="description">
    </head>
</html>"""
META4 = """
<html>
    <head>
        <h1>h1</h1>
        <title>title</title>
    </head>
</html>"""


@pytest.mark.parametrize(
    "url, result",
    [
        (META1, ("h1", "title", "description")),
        (META2, ("", "title", "description")),
        (META3, ("h1", "", "description")),
        (META4, ("h1", "title", "")),
    ],
)
def test_get_content(url, result):
    assert get_content(url) == result
