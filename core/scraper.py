from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os
import requests

from . import config
from . import utils

class OpenFoodFactsScraper:
    def __init__(self):
        # Configurar Selenium usando las opciones definidas en config
        self.options = Options()
        for arg in config.SELENIUM_OPTIONS:
            self.options.add_argument(arg)
        # Inicializar el driver de Chrome utilizando webdriver_manager
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        # Lista para almacenar las filas que se escribirán en el CSV
        self.rows = []
    
    def get_categories(self):
        # Mostrar mensaje y obtener la página de categorías
        print("[?] Obteniendo categorías disponibles...")
        self.driver.get(config.CATEGORIAS_URL)
        time.sleep(3)
        # Parsear el HTML con BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        categorias = []
        # Seleccionar cada fila de la tabla de categorías
        filas_categoria = soup.select("table#tagstable tbody tr")
        for fila in filas_categoria:
            celdas = fila.select("td")
            if len(celdas) >= 1:
                # Buscar el primer enlace de la fila
                primer_enlace = celdas[0].find("a")
                if primer_enlace:
                    href = primer_enlace.get("href", "")
                    nombre = primer_enlace.get_text(strip=True)
                    # Validar que el enlace corresponde a una categoría válida
                    if href.startswith("/facets/categorias/") or href.startswith("/categoria/"):
                        url_categoria = config.BASE_URL + href
                        categorias.append((nombre, url_categoria))
        print(f"[✔] {len(categorias)} categorías encontradas.")
        # Aplicar límite de categorías si está configurado
        if config.LIMITE_CATEGORIAS:
            categorias = categorias[:config.LIMITE_CATEGORIAS]
        return categorias

    def scrape(self):
        categorias = self.get_categories()
        # Recorrer cada categoría obtenida
        for nombre_categoria, url_categoria_base in categorias:
            print(f"\n[...] Procesando categoría: {nombre_categoria}")
            # Iterar sobre las páginas de la categoría
            for pagina in range(1, (config.LIMITE_PAGINAS or 1) + 1):
                url = url_categoria_base if pagina == 1 else f"{url_categoria_base}/{pagina}"
                print(f"  [WEB] Página {pagina}: {url}")
                self.driver.get(url)
                time.sleep(3)
                # Parsear la página de productos
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                productos = soup.select("a.list_product_a")
                if not productos:
                    print("  [X] No se encontraron productos en esta página.")
                    break
                producto_num = 1
                # Recorrer cada producto listado en la página
                for producto in productos:
                    if config.LIMITE_PRODUCTOS and producto_num > config.LIMITE_PRODUCTOS:
                        print("  [LIMIT] Límite de productos por página alcanzado.")
                        break
                    if config.SHOW_FEEDBACK:
                        print(f"    - Producto #{producto_num}")
                    producto_num += 1
                    try:
                        # Extraer el nombre del producto desde la lista
                        nombre_el = producto.select_one(".list_product_name")
                        nombre = nombre_el.text.strip() if nombre_el else ""
                        url_producto = producto["href"]
                        url_completa = f"{config.BASE_URL}{url_producto}" if not url_producto.startswith("http") else url_producto

                        # Cargar la página individual del producto
                        self.driver.get(url_completa)
                        time.sleep(1)
                        producto_soup = BeautifulSoup(self.driver.page_source, "html.parser")
                        
                        # Extraer la marca
                        marca_el = producto_soup.select_one("span#field_brands_value")
                        marca = marca_el.text.strip() if marca_el else ""
                        
                        # Extraer los ingredientes
                        ing_el = producto_soup.select_one("#panel_ingredients_content .panel_text")
                        ingredientes = ing_el.text.strip() if ing_el else ""
                        
                        # Extraer los alérgenos buscando en paneles de texto
                        alergenos = ""
                        for panel in producto_soup.select("div.panel_text"):
                            strong_tag = panel.find("strong")
                            if strong_tag and "alérgenos" in strong_tag.text.lower():
                                alergenos = panel.get_text().replace(strong_tag.text, "").strip().strip(":")
                                break
                        
                        # Extraer información nutricional de la tabla correspondiente
                        nutricion = ""
                        tabla_nutricion = producto_soup.select_one("#panel_nutrition_facts_table_content table")
                        if tabla_nutricion:
                            filas_nutricion = tabla_nutricion.select("tr")
                            partes = []
                            for fila_nut in filas_nutricion:
                                columnas = fila_nut.select("td")
                                texto_fila = " | ".join(col.text.strip().replace("\xa0", " ") for col in columnas if col.text.strip())
                                if texto_fila:
                                    partes.append(texto_fila)
                            nutricion = " || ".join(partes)

                        # Extraer tiendas donde se vende el producto
                        stores_el = producto_soup.select_one("span#field_stores_value")
                        if stores_el:
                            store_links = stores_el.select("a")
                            # Unir múltiples tiendas si existen
                            tiendas = ", ".join(link.get_text(strip=True) for link in store_links)
                        else:
                            tiendas = ""

                        # Extraer origen de los ingredientes
                        # <span class="field_value" id="field_origins_value"> ... </span>
                        origen_el = producto_soup.select_one("#field_origins_value")
                        origen = origen_el.text.strip() if origen_el else ""   

                        # Extraer países de venta
                        # <span class="field_value" id="field_countries_value">"
                        countries_el = producto_soup.select_one("#field_countries_value")
                        paises_venta = countries_el.text.strip() if countries_el else ""

                        # Extraer codigo de barras
                        barcode_el = producto_soup.select_one("#barcode")
                        codigo_barras = barcode_el.text.strip() if barcode_el else ""                        
                        
                        # Añadir la fila con todos los campos extraídos al dataset
                        self.rows.append([
                            nombre,
                            marca,
                            ingredientes,
                            alergenos,
                            nutricion,
                            origen,
                            url_completa,
                            nombre_categoria,
                            tiendas,
                            paises_venta,
                            codigo_barras
                        ])
                    
                    except Exception as e:
                        error_msg = f"[WARN] Error al procesar producto: {url_completa}\n→ {str(e)}\n"
                        print(error_msg)
                        utils.log_error(config.LOG_FILENAME, error_msg)
                        continue
                # Verificar el límite de páginas configurado
                if config.LIMITE_PAGINAS and pagina >= config.LIMITE_PAGINAS:
                    print("  [LIMIT] Límite de páginas alcanzado (modo pruebas).")
                    break

    def save_to_csv(self):
        # Guardar todas las filas recopiladas en un archivo CSV con las respectivas cabeceras
        with open(config.CSV_FILENAME, mode="w", encoding="utf-8-sig", newline="") as archivo:
            writer = csv.writer(archivo)
            writer.writerow([
                "Nombre",
                "Marca",
                "Ingredientes",
                "Alergenos",
                "Nutricion",
                "Origen",
                "URL",
                "Categoria",
                "Tiendas",
                "Paises de Venta",
                "Codigo de barras"
            ])
            writer.writerows(self.rows)
        print(f"\n[✔] CSV completo generado y guardado correctamente en {config.CSV_FILENAME}")

    def close(self):
        # Cerrar el navegador para liberar recursos
        self.driver.quit()

def run_scraper():
    # Inicializar el log de errores
    utils.init_log(config.LOG_FILENAME)
    # Instanciar y ejecutar el scraper
    scraper = OpenFoodFactsScraper()
    scraper.scrape()
    scraper.save_to_csv()
    scraper.close()
    # Cerrar el log de errores
    utils.close_log(config.LOG_FILENAME)
