from page_analyzer.app import get_content
import pytest


@pytest.mark.parametrize("url, result", [
    (
        'tests/fixtures/test_meta1.html',
        ('h1', 'title', 'description'),
    ),
    (
        'tests/fixtures/test_meta2.html',
        ('', 'title', 'description'),
    ),
    (
        'tests/fixtures/test_meta3.html',
        ('h1', '', 'description'),
    ),
    (
        'tests/fixtures/test_meta4.html',
        ('h1', 'title', ''),
    )
    ]
)
def test_get_content(url, result):
    with open(url) as file:
        data = file.read()
    assert get_content(data) == result
