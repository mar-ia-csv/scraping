import os

# Configuración de Selenium
SELENIUM_OPTIONS = [
    "--headless",
    "--disable-gpu",
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

# Configuraciones de scraping
LIMITE_CATEGORIAS = 60      # Limita la cantidad de categorías (None para todas)
LIMITE_PAGINAS = 1          # Número de páginas por categoría
LIMITE_PRODUCTOS = 50      # Número de productos por página
SHOW_FEEDBACK = True       # Mostrar mensajes de avance

# URLs y paths
BASE_URL = "https://es.openfoodfacts.org"
CATEGORIAS_URL = BASE_URL + "/facets/categorias"

# Output
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')

# Asegurar que existe el directotio output
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Paths
CSV_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'scraped_products.csv'))
LOG_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'errores.log'))
