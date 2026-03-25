"""Test that requests library works."""

from vibe_flow.logger import logger
import requests

url = "https://httpbin.org/get"
logger.info(f"GET {url}")

response = requests.get(url)
logger.info(f"Status: {response.status_code}")
logger.debug(f"Headers: {dict(response.headers)}")

data = response.json()
print(f"Your IP: {data['origin']}")
print(f"Status: {response.status_code}")
