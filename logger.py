# logger.py
from datetime import datetime

# Clase para guardar los eventos y errores en el archivo .log
class RegistradorLogs:
    def __init__(self, archivo="eventos_sistema.log"):
        self.archivo = archivo

    def registrar_evento(self, nivel, mensaje):
        hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        texto_log = f"[{hora}] [{nivel}] {mensaje}\n"
        f = None

        try:
            # Abrimos en modo 'a' para ir agregando líneas sin borrar lo anterior
            f = open(self.archivo, "a", encoding="utf-8")
            f.write(texto_log)
        except Exception as e:
            print("No se pudo escribir en el archivo de logs:", e)
        finally:
            # Siempre cerramos el archivo aunque ocurra un fallo
            if f is not None:
                f.close()
