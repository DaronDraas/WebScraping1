import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

baseUrl = "https://listado.mercadolibre.cl"
searchUrl = "https://listado.mercadolibre.cl/inmuebles/departamentos/arriendo/_Desde_{}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
}
productlinks = set()  # Usamos un conjunto para evitar duplicados

# Obtener enlaces de la primera página
first_page_url = "https://listado.mercadolibre.cl/inmuebles/departamentos/arriendo/_NoIndex_True"
r = requests.get(first_page_url, headers=headers)
if r.status_code == 200:
    soup = BeautifulSoup(r.content, "lxml")
    productlist = soup.find_all("a", class_="andes-pagination__link")
    for link in productlist:
        href = link.get("href", "")
        if href:
            productlinks.add(href)

# Obtener enlaces de las páginas siguientes
page = 2
increment = 48

while True:
    offset = (page - 1) * increment + 1
    url = searchUrl.format(offset)
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        break  # Si hay un error en la solicitud, detener el bucle
    
    soup = BeautifulSoup(r.content, "lxml")
    productlist = soup.find_all("a", class_="andes-pagination__link")
    
    if not productlist:
        break  # Si no hay productos en la página, detener el bucle
    
    for link in productlist:
        href = link.get("href", "")
        if href:
            productlinks.add(href)
    
    page += 1

print(f"Total product links: {len(productlinks)}")
productlinks_list = list(productlinks)
print(productlinks_list)

lista_arriendos = []
for link in productlinks:
    r = requests.get(link, headers=headers)
    if r.status_code != 200:
        continue  # Si hay un error en la solicitud, omitir este link
    soup = BeautifulSoup(r.content, "lxml")
    productitem = soup.find_all("a", class_="ui-search-link__title-card ui-search-link")
    for link in productitem:
        href = link.get("href", "")
        if href:
            lista_arriendos.append(href)

lista_arriendos_lista = list(lista_arriendos)
print(lista_arriendos_lista)

detalle_vivienda = []
for link in lista_arriendos:
    r = requests.get(link, headers=headers)
    if r.status_code != 200:
        continue  # Si hay un error en la solicitud, omitir este link
    soup = BeautifulSoup(r.content, "lxml")
    items = soup.find_all("div", class_="ui-pdp-container ui-pdp-container--pdp")

    for item in items:
        try:
            description = item.find("h1", class_="ui-pdp-title").text.strip()
        except AttributeError:
            description = ""

        try:
            location = item.find("a", class_="ui-pdp-color--BLUE ui-pdp-size--XSMALL ui-pdp-family--REGULAR ui-pdp-seller-validated__title").text.strip()
        except AttributeError:
            location = ""

        try:
            price = item.find("span", class_="andes-money-amount__fraction").text.strip()
        except AttributeError:
            price = ""

        arriendo = {
            "description": description,
            "location": location,
            "price": price
        }

        detalle_vivienda.append(arriendo)
        print(f"Saving: {arriendo['description']}, {arriendo['location']}, {arriendo['price']}")

df = pd.DataFrame(detalle_vivienda)
print(df)
#df.to_csv('Arriendos_detalle.csv', index=False, quoting=csv.QUOTE_ALL, encoding='utf-8', sep=';')