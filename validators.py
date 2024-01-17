import validators
import requests


def is_valid_url(url):
    if not validators.url(url):
        return False

    try:
        response = requests.head(url)
        return response.status_code == requests.codes.ok
    except requests.RequestException:
        return False
