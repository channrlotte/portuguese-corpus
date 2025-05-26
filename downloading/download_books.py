import json
import os.path
import requests
import time

from fake_useragent import UserAgent
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from chatgpt import process_request

proxies_vars = []
with open("proxy_List.json", "rt") as inp:
    js = json.load(inp)

for proxy in js:
    if "http" in proxy["protocols"]:
        proxies_vars.append("http://" + proxy["ip"] + ":" + proxy["port"])

REPLACE_MAPPING = {
    "à": "a",
    "á": "a",
    "ã": "a",
    "ä": "a",
    "å": "a",
    "â": "a",
    "ç": "c",
    "è": "e",
    "é": "e",
    "ê": "e",
    "ë": "e",
    "é": "e",
    "í": "i",
    "ï": "i",
    "ñ": "n",
    "ó": "o",
    "ô": "o",
    "ö": "o",
    "õ": "o",
    "œ": "oe",
    "š": "s",
    "ú": "u",
    "ü": "u",
    "ū": "u",
    "ý": "y",
    "": "",
}


class Author:
    def __init__(self, name: str):
        self.name = name.strip().lower()
        for replace_from, replace_to in REPLACE_MAPPING.items():
            self.name = self.name.replace(replace_from, replace_to)

    @property
    def is_portuguese(self):
        return process_request(self.name)

    def __repr__(self):
        return f"Author({self.name})"


class Book:
    def __init__(self, source):
        if isinstance(source, tuple):
            self.md5 = source[0].strip()
            self.title = source[1].strip()
            self.authors = [
                Author(author_name.strip()) for author_name in source[2].split(";")
            ]
            self.extension = source[3]

        elif isinstance(source, dict):
            self.md5 = source["md5"].strip()
            self.title = source["title"].strip()
            self.authors = [
                Author(author_name.strip())
                for author_name in source["author"].split(";")
            ]
            self.extension = source["extension"]

        else:
            raise RuntimeError(f"Unsupported format: {source}")

    @property
    def is_portuguese(self):
        return all(author.is_portuguese for author in self.authors)

    @property
    def path(self):
        return f"data/{self.extension}/{self.md5}.{self.extension}"

    def __repr__(self):
        return f"Book({self.md5=}, {self.title=}, {self.authors=}, {self.extension=})"


cur_proxy = 0


def load_book(book: Book) -> bool:
    global cur_proxy

    if os.path.exists(book.path):
        return True

    url = "http://cdn3.booksdl.lc/get.php?md5=" + book.md5
    ua = UserAgent()
    my_id = cur_proxy
    proxy = proxies_vars[my_id]
    proxies = {"http": proxy, "https": proxy}

    try:
        r = requests.get(
            url, {"User-Agent": str(ua.random)}, proxies=proxies, timeout=5
        )
    except Exception:
        cur_proxy += 1
        return False

    if (
        r.status_code != 200
        or not r.ok
        or int(r.headers.get("Content-Length")) != len(r.content)
    ):
        cur_proxy += 1
        cur_proxy %= len(proxies_vars)
        return False

    cur_proxy = my_id

    with open(book.path, "wb") as out:
        out.write(r.content)

    return True


if __name__ == "__main__":
    with open("books.json", "rt", encoding="utf-8") as inp:
        book_sources = json.load(inp)
    books = [Book(book_source) for book_source in book_sources]

    all_extensions = set(book.extension for book in books)

    if not os.path.exists("data"):
        os.mkdir("data")

    for extension in all_extensions:
        path = f"data/{extension}"
        if not os.path.exists(path):
            os.mkdir(path)

    books = deque([book for book in books if not os.path.exists(book.path)])

    while len(books) > 0:
        pbar = tqdm(total=len(books))

        with ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(lambda book: pbar.update() if load_book(book) else None, books)
        pbar.close()

        books = deque([book for book in books if not os.path.exists(book.path)])

    books = deque(books)

    while len(books) > 0:
        book = books[0]
        books.popleft()

        if os.path.exists(book.path):
            continue

        if load_book(book):
            pbar.set_description("Loaded successfully")
            pbar.update()
            continue

        else:
            pbar.set_description(f"Failed to load")
            books.append(book)
            time.sleep(1)
