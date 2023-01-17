import asyncio
import csv
import itertools
import logging
import os
from typing import Callable, Iterable, Optional, TypeVar

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://gratka.pl/"
OFFERS_PATH = "nieruchomosci/mieszkania"
OUTFILE = "out.csv"
CHUNK_SIZE = 1


T = TypeVar("T")


def chunks(n: int, iterable: Iterable[T]):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


async def scrape(page_limit: Optional[int] = None):
    logging.info("Starting...")
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        page_count = (
            await scrape_page_count(client) if page_limit is None else page_limit
        )

        fields = [
            "tytuł",
            "miasto",
            "adres",
            "powierzchnia",
            "liczba pokoi",
            "piętro",
            "rok budowy",
            "data dodania",
            "data zaktualizowania",
            "cena",
            "cena/m2",
            "opis",
            "link",
        ]

        with open(OUTFILE, "x", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=fields, dialect=csv.excel, restval=""
            )
            writer.writeheader()

            for work_chunk in chunks(CHUNK_SIZE, range(1, page_count + 1)):
                for future in asyncio.as_completed(
                    tuple(scrape_offers_page(client, i) for i in work_chunk)
                ):
                    offers = await future
                    writer.writerows(offers)

        logging.info("Finished!")


async def scrape_page_count(client: httpx.AsyncClient) -> int:
    resp = await client.get(OFFERS_PATH)
    root_page = BeautifulSoup(resp.text, "lxml")
    return int(
        root_page.find("a", class_="pagination__nextPage").find_previous("a").text
    )


async def scrape_offers_page(
    client: httpx.AsyncClient, page_num: int
) -> list[dict[str, str]]:
    offers_resp = await client.get(OFFERS_PATH, params={"page": page_num})
    offers_page = BeautifulSoup(offers_resp.text, "lxml")

    offers = await asyncio.gather(
        *(
            scrape_offer_details(client, div.find("a", class_="teaserLink")["href"])
            for div in offers_page.find_all("div", class_="listing__teaserWrapper")
        )
    )
    logging.info(f"Page {page_num} done")
    return offers


async def scrape_offer_details(client: httpx.AsyncClient, link: str) -> dict[str, str]:
    specs_resp = await client.get(link)
    specs_page = BeautifulSoup(specs_resp.text, "lxml")
    offer = {"link": link}

    offer["tytuł"] = specs_page.find("h1", class_="sticker__title").text.strip()

    if (text := specs_page.find("span", class_="priceInfo__value").text.strip()).find(
        "Zapytaj o cenę"
    ) == -1:
        offer["cena"] = text.splitlines()[0].strip()

    if (span := specs_page.find("span", class_="priceInfo__additional")) is not None:
        offer["cena/m2"] = " ".join(span.text.strip().splitlines()[0].split(" ")[:-1])

    if len((split := offer["tytuł"].split(","))) > 1:
        offer["adres"] = split[-1].strip()

    if (div := specs_page.find("div", class_="description__rolled")) is not None:
        offer["opis"] = div.text.strip()

    specs_list = [
        li.find_all()
        for li in specs_page.find("ul", class_="parameters__singleParameters").find_all(
            "li"
        )
    ]

    def scrape_spec(
        key: str,
        search: str,
        mapper: Optional[Callable[[str], str]] = None,
    ):
        for cell in specs_list:
            if cell[0].text.find(search) != -1:
                value = cell[1].text.strip()
                offer[key] = value if mapper is None else mapper(value).strip()

    scrape_spec("miasto", "Lokalizacja", lambda t: t.split(",")[0])
    scrape_spec("powierzchnia", "Powierzchnia w m2", lambda t: t.split(" ")[0])
    scrape_spec("liczba pokoi", "Liczba pokoi")
    scrape_spec("piętro", "Piętro")
    scrape_spec("rok budowy", "Rok budowy")
    scrape_spec("data dodania", "Dodane")
    scrape_spec("data zaktualizowania", "Zaktualizowane")

    return offer


def main():
    logging.basicConfig(
        format="%(levelname)s: %(asctime)s - %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
    )

    try:
        os.remove(OUTFILE)
    except FileNotFoundError:
        pass

    asyncio.run(scrape(20))


if __name__ == "__main__":
    main()
