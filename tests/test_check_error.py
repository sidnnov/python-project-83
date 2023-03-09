from page_analyzer.app import check_error, app
import pytest


@pytest.mark.parametrize(
    "url, correct_answer",
    [
        ("", [("danger", "Некорректный URL"), ("danger", "URL обязателен")]),
        ("htps://bad_example.com/", [("danger", "Некорректный URL")]),
        ("https://example.com/" + "x" * 250, [(
            "danger", "URL превышает 255 символов")]),
        (
            "htps://bad_example.com/" + "x" * 250,
            [
                ("danger", "Некорректный URL"),
                ("danger", "URL превышает 255 символов"),
            ],
        ),
    ],
)
def test_check_error(url, correct_answer):
    with app.test_request_context():
        messages = check_error(url)
        assert correct_answer == messages
