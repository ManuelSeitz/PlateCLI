import argparse
import os
import random
from time import sleep

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from src.utils.constants import COUNTRIES


def scrap_images(country: str, limit: int = 100):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)

    if country not in COUNTRIES:
        raise KeyError("País no disponible.")

    city = COUNTRIES[country]

    print(f"Creando la carpeta {country} en images...")

    images_path = os.path.join("images", country.replace(" ", "-"))
    os.makedirs(images_path, exist_ok=True)

    count = 0
    query = "carros" if country == "brazil" else "autos"

    sleep(2)
    url = f"https://www.google.com/search?q=site:facebook.com/marketplace/{city}+{query}&tbm=isch"
    driver.get(url)
    sleep(2)

    try:
        see_more_btn = driver.find_element(By.CSS_SELECTOR, "a[jsaction='ix6FRc']")
        see_more_btn.click()
    except NoSuchElementException:
        pass

    for _ in range(6):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # type: ignore
        sleep(random.uniform(2, 5))

    links = driver.find_elements(
        By.CSS_SELECTOR,
        f"div[jsname='dTDiAc'] a[href^='https://www.facebook.com/marketplace/{city}/']",
    )
    marketplace_links = list({link.get_attribute("href") for link in links})[:60]  # type: ignore

    downloaded_items: set[str] = set()

    for marketplace_url in marketplace_links:
        if not marketplace_url:
            continue
        driver.get(marketplace_url)
        sleep(2)

        items = driver.find_elements(By.CSS_SELECTOR, "a[href^='/marketplace/item']")
        item_links = [item.get_attribute("href") for item in items[:5]]  # type: ignore

        for item_url in item_links:
            if not item_url or item_url in downloaded_items:
                continue
            if len(downloaded_items) == limit:
                print(f"Límite alcanzado: {limit} imágenes descargadas.")
                return
            driver.get(item_url)
            sleep(2)

            try:
                image = driver.find_element(
                    By.CSS_SELECTOR, "img.xz74otr[src^='https://scontent']"
                )
                image_url = image.get_attribute("src")  # type: ignore
                if not image_url:
                    continue
                file_name = f"{country}-{count}.jpg"
                image_path = os.path.join(images_path, file_name)
                print(f"Descargando {image_url}...")
                response = requests.get(image_url, timeout=5)
                if response.status_code == 200:
                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    downloaded_items.add(item_url)
                count += 1
            except Exception as e:
                print(f"No se pudo descargar la imagen: {e}")
    driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descarga imágenes de matrículas")
    parser.add_argument("--limit", type=int, default=100)

    args = parser.parse_args()

    for c in COUNTRIES:
        scrap_images(country=c, limit=args.limit)
        sleep(10)
