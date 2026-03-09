from datetime import datetime

from bs4 import BeautifulSoup


def strip_html(html_contents: str) -> str:
    """
    takes out html tags from a job description string.
    """
    soup = BeautifulSoup(html_contents, "lxml")
    text = soup.get_text(separator="\n", strip=True)
    return text


def parse_datetimes(datetime_str: str) -> datetime:
    datetime_obj = datetime.fromisoformat(datetime_str[:-1])
    return datetime_obj


def send_email_via_smtp(subject: str, body: str):
    pass
