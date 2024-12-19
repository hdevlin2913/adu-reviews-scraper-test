import random
import string

from fake_useragent import UserAgent


def get_headers() -> dict[str, str]:
    random_request_id = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=180)
    )
    ua = UserAgent(
        browsers=["Google", "Chrome", "Firefox", "Edge"],
        os=["Windows", "Linux", "Ubuntu"],
        platforms=["desktop"],
    )
    return {
        "X-Requested-By": random_request_id,
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
        "Referer": "https://www.tripadvisor.com",
        "Origin": "https://www.tripadvisor.com",
        "DNT": "1",
    }
