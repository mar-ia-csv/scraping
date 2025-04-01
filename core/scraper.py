from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

from . import config
from . import utils

class OpenFoodFactsScraper:
    def __init__(self):
        # Configurar Selenium con las opciones definidas en config
        self.options = Options()
        for arg in config.SELENIUM_OPTIONS:
            self.options.add_argument(arg)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.rows = []
    
    def get_categories(self):
        print("[?] Obteniendo categorías disponibles...")
        self.driver.get(config.CATEGORIAS_URL)
        time.sleep(3)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        categorias = []
        filas_categoria = soup.select("table#tagstable tbody tr")
        for fila in filas_categoria:
            celdas = fila.select("td")
            if len(celdas) >= 1:
                primer_enlace = celdas[0].find("a")
                if primer_enlace:
                    href = primer_enlace.get("href", "")
                    nombre = primer_enlace.get_text(strip=True)
                    if href.startswith("/facets/categorias/") or href.startswith("/categoria/"):
                        url_categoria = config.BASE_URL + href
                        categorias.append((nombre, url_categoria))
        print(f"[✔] {len(categorias)} categorías encontradas.")
        if config.LIMITE_CATEGORIAS:
            categorias = categorias[:config.LIMITE_CATEGORIAS]
        return categorias

    def scrape(self):
        categorias = self.get_categories()
        for nombre_categoria, url_categoria_base in categorias:
            print(f"\n[...] Procesando categoría: {nombre_categoria}")
            for pagina in range(1, (config.LIMITE_PAGINAS or 1) + 1):
                url = url_categoria_base if pagina == 1 else f"{url_categoria_base}/{pagina}"
                print(f"  [WEB] Página {pagina}: {url}")
                self.driver.get(url)
                time.sleep(3)
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                productos = soup.select("a.list_product_a")
                if not productos:
                    print("  [X] No se encontraron productos en esta página.")
                    break
                producto_num = 1
                for producto in productos:
                    if config.LIMITE_PRODUCTOS and producto_num > config.LIMITE_PRODUCTOS:
                        print("  [LIMIT] Límite de productos por página alcanzado.")
                        break
                    if config.SHOW_FEEDBACK:
                        print(f"    - Producto #{producto_num}")
                    producto_num += 1
                    try:
                        nombre_el = producto.select_one(".list_product_name")
                        nombre = nombre_el.text.strip() if nombre_el else ""
                        url_producto = producto["href"]
                        url_completa = f"{config.BASE_URL}{url_producto}" if not url_producto.startswith("http") else url_producto
                        # Cargar producto
                        self.driver.get(url_completa)
                        time.sleep(1)
                        producto_soup = BeautifulSoup(self.driver.page_source, "html.parser")
                        # Marca
                        marca_el = producto_soup.select_one("span#field_brands_value")
                        marca = marca_el.text.strip() if marca_el else ""
                        # Ingredientes
                        ing_el = producto_soup.select_one("#panel_ingredients_content .panel_text")
                        ingredientes = ing_el.text.strip() if ing_el else ""
                        # Alérgenos
                        alergenos = ""
                        for panel in producto_soup.select("div.panel_text"):
                            strong_tag = panel.find("strong")
                            if strong_tag and "alérgenos" in strong_tag.text.lower():
                                alergenos = panel.get_text().replace(strong_tag.text, "").strip().strip(":")
                                break
                        # Nutrición
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
                        self.rows.append([nombre, marca, ingredientes, alergenos, nutricion, url_completa, nombre_categoria])
                    except Exception as e:
                        error_msg = f"[WARN] Error al procesar producto: {url_completa}\n→ {str(e)}\n"
                        print(error_msg)
                        utils.log_error(config.LOG_FILENAME, error_msg)
                        continue
                if config.LIMITE_PAGINAS and pagina >= config.LIMITE_PAGINAS:
                    print("  [LIMIT] Límite de páginas alcanzado (modo pruebas).")
                    break

    def save_to_csv(self):
        with open(config.CSV_FILENAME, mode="w", encoding="utf-8", newline="") as archivo:
            writer = csv.writer(archivo)
            writer.writerow(["Nombre", "Marca", "Ingredientes", "Alergenos", "Nutricion", "URL", "Categoria"])
            writer.writerows(self.rows)
        print(f"\n[✔] CSV completo generado y guardado correctamente en {config.CSV_FILENAME}")

    def close(self):
        self.driver.quit()

def run_scraper():
    # Inicializar log
    utils.init_log(config.LOG_FILENAME)
    # Instanciar y ejecutar el scraper
    scraper = OpenFoodFactsScraper()
    scraper.scrape()
    scraper.save_to_csv()
    scraper.close()
    # Cerrar el log
    utils.close_log(config.LOG_FILENAME)
