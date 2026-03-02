import re
import sys
import csv
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup, NavigableString

URL = "https://www.maisgasolina.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

FUELS = {
    "Gasolina 95 Simples": "Gasolina 95 Simples",
    "Gasolina 98 Simples": "Gasolina 98 Simples",
    "Gasóleo Simples": "Gasóleo Simples",
    "Gasóleo +": "Gasóleo +",
    "GPL Auto": "GPL Auto",
}


def get_prices():
    r = requests.get(URL, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    section = soup.find(id="homeAverage")
    if not section:
        print("precos não encontrada.")
        sys.exit(1)

    results = []
    for name, value in zip(section.select(".homePricesName"), section.select(".homePricesValue")):
        fuel = name.get_text(strip=True)
        if fuel not in FUELS:
            continue
        for node in value.children:
            if isinstance(node, NavigableString):
                text = str(node).strip().replace("\xa0", "").replace("\u20ac", "").replace(",", ".")
                if re.match(r"^\d+\.\d+$", text):
                    results.append((FUELS[fuel], float(text)))
                    break

    return results


def save(results):
    Path("output").mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path("output") / f"precos_{ts}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["combustivel", "preco", "data_hora"])
        for fuel, price in results:
            writer.writerow([fuel, price, datetime.now().isoformat()])
    print(f"Guardado: {path}")


if __name__ == "__main__":
    results = get_prices()
    print(f"\nPreços médios - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    for fuel, price in results:
        print(f"  {fuel:<20} {price:.3f} EUR")
    print()
    save(results)
