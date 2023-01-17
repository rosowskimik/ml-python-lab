import csv
from typing import Callable, Optional

import requests
from bs4 import BeautifulSoup

LINK = "https://gratka.pl/nieruchomosci/mieszkania"


def scrape(page_limit: Optional[int] = None):
    with requests.session() as s:
        if page_limit is None:
            root_page = BeautifulSoup(s.get(LINK).text, "html.parser")
            page_count = int(
                root_page.find("a", class_="pagination__nextPage")
                .find_previous("a")
                .text
            )
        else:
            page_count = page_limit

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
        with open("out.csv", "x", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=fields, dialect=csv.excel, restval=""
            )
            writer.writeheader()

            for i in range(1, page_count + 1):
                print(f"Scraping offers from {i} page")
                page_link = f"{LINK}?page={i}"
                offer_page = BeautifulSoup(s.get(page_link).text, "html.parser")

                for j, link in enumerate(
                    div.find("a", class_="teaserLink")["href"]
                    for div in offer_page.find_all(
                        "div", class_="listing__teaserWrapper"
                    )
                ):
                    print(f"\tScraping offer {(i-1)*32 + j + 1}")
                    specs_page = BeautifulSoup(s.get(link).text, "html.parser")
                    offer = {"link": link}

                    offer["tytuł"] = specs_page.find(
                        "h1", class_="sticker__title"
                    ).text.strip()

                    if (
                        text := specs_page.find(
                            "span", class_="priceInfo__value"
                        ).text.strip()
                    ).find("Zapytaj o cenę") == -1:
                        offer["cena"] = text.splitlines()[0].strip()

                    if (
                        span := specs_page.find("span", class_="priceInfo__additional")
                    ) is not None:
                        offer["cena/m2"] = " ".join(
                            span.text.strip().splitlines()[0].split(" ")[:-1]
                        )

                    if len((split := offer["tytuł"].split(","))) > 1:
                        offer["adres"] = split[-1].strip()

                    if (
                        div := specs_page.find("div", class_="description__rolled")
                    ) is not None:
                        offer["opis"] = div.text.strip()

                    specs_list = [
                        li.find_all()
                        for li in specs_page.find(
                            "ul", class_="parameters__singleParameters"
                        ).find_all("li")
                    ]

                    def scrape_spec(
                        key: str,
                        search: str,
                        mapper: Optional[Callable[[str], str]] = None,
                    ):
                        for cell in specs_list:
                            if cell[0].text.find(search) != -1:
                                value = cell[1].text.strip()
                                offer[key] = (
                                    value if mapper is None else mapper(value).strip()
                                )

                    scrape_spec("miasto", "Lokalizacja", lambda t: t.split(",")[0])
                    scrape_spec(
                        "powierzchnia", "Powierzchnia w m2", lambda t: t.split(" ")[0]
                    )
                    scrape_spec("liczba pokoi", "Liczba pokoi")
                    scrape_spec("piętro", "Piętro")
                    scrape_spec("rok budowy", "Rok budowy")
                    scrape_spec("data dodania", "Dodane")
                    scrape_spec("data zaktualizowania", "Zaktualizowane")

                    writer.writerow(offer)

        print("DONE!!!")


if __name__ == "__main__":
    scrape(2)
