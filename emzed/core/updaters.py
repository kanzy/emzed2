# encoding:latin-1

from config import global_config
import requests

def get_latest_emzed_version_from_pypi():
    url = global_config.get_url("pypi_url")
    response = requests.get(url + "emzed/json")
    response.raise_for_status()
    version_str = response.json()["info"]["version"]
    return tuple(map(int, version_str.split(".")))
