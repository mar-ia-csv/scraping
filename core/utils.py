import datetime

def init_log(filename):
    """Inicializa el archivo de log con un encabezado."""
    with open(filename, "w", encoding="utf-8") as log_file:
        log_file.write("Registro de errores - Open Food Facts Scraper\n")
        log_file.write(f"Inicio: {datetime.datetime.now()}\n\n")

def log_error(filename, message):
    """Escribe un mensaje de error en el log."""
    with open(filename, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def close_log(filename):
    """Finaliza el log con la marca de tiempo de cierre."""
    with open(filename, "a", encoding="utf-8") as log_file:
        log_file.write(f"Fin: {datetime.datetime.now()}\n")
