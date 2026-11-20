# entidades.py
from abc import ABC, abstractmethod
from datetime import datetime
from excepciones import DatosInvalidosError
from logger import RegistradorLogs

# Clase abstracta general de la que heredan las demás entidades
class EntidadSistema(ABC):
    def __init__(self, id_entidad):
        if not id_entidad or str(id_entidad).strip() == "":
            raise DatosInvalidosError("El ID no puede quedar vacío.")
        self._id_entidad = str(id_entidad).strip()
        self._fecha_registro = datetime.now()

    @property
    def id_entidad(self):
        return self._id_entidad

    @property
    def fecha_registro(self):
        return self._fecha_registro

    @abstractmethod
    def validar(self):
        pass

    @abstractmethod
    def obtener_info(self):
        pass


# Clase Cliente con datos encapsulados y validaciones
class Cliente(EntidadSistema):
    def __init__(self, documento, nombre, correo, telefono, logger=None):
        super().__init__(documento)

        if logger is None:
            self.logger = RegistradorLogs()
        else:
            self.logger = logger

        # Atributos privados para aplicar encapsulación
        self.__documento = ""
        self.__nombre = ""
        self.__correo = ""
        self.__telefono = ""

        # Pasamos cada dato por su setter para validarlo
        self.documento = documento
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

        self.logger.registrar_evento("INFO", f"Cliente creado: {self.__nombre} - CC: {self.__documento}")

    @property
    def documento(self):
        return self.__documento

    @documento.setter
    def documento(self, valor):
        try:
            dato = str(valor).strip()
            num = int(dato)
        except ValueError as err:
            # Encadenamiento de excepciones por si escriben letras en el documento
            msg = f"El documento '{valor}' no es válido, solo se aceptan números."
            self.logger.registrar_evento("ERROR", msg)
            raise DatosInvalidosError(msg) from err
        else:
            if num <= 0 or len(dato) < 6:
                msg = f"El documento '{dato}' debe ser positivo y tener mínimo 6 dígitos."
                self.logger.registrar_evento("ERROR", msg)
                raise DatosInvalidosError(msg)
            self.__documento = dato

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        dato = str(valor).strip() if valor is not None else ""
        if len(dato) < 3:
            msg = f"El nombre '{valor}' es muy corto, mínimo 3 letras."
            self.logger.registrar_evento("ERROR", msg)
            raise DatosInvalidosError(msg)
        self.__nombre = dato

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        dato = str(valor).strip() if valor is not None else ""
        if "@" not in dato or "." not in dato:
            msg = f"El correo '{valor}' no tiene un formato válido."
            self.logger.registrar_evento("ERROR", msg)
            raise DatosInvalidosError(msg)
        self.__correo = dato

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        dato = str(valor).strip() if valor is not None else ""
        if not dato.isdigit() or len(dato) < 7 or len(dato) > 10:
            msg = f"El teléfono '{valor}' debe tener entre 7 y 10 números."
            self.logger.registrar_evento("ERROR", msg)
            raise DatosInvalidosError(msg)
        self.__telefono = dato

    def validar(self):
        if self.__documento != "" and self.__nombre != "" and self.__correo != "" and self.__telefono != "":
            return True
        return False

    def obtener_info(self):
        return f"Cliente: {self.__nombre} | CC: {self.__documento} | Correo: {self.__correo} | Tel: {self.__telefono}"


# Pruebas rápidas para verificar que esta parte funciona antes de subirla
if __name__ == "__main__":
    log = RegistradorLogs()

    # Prueba con cliente válido
    try:
        c1 = Cliente("1095823412", "Camila Torres", "camila.torres@gmail.com", "3124567890", log)
        print("OK ->", c1.obtener_info())
    except DatosInvalidosError as e:
        print("Error:", e)

    # Prueba con cliente inválido (debe atrapar el error sin detener el programa)
    try:
        c2 = Cliente("999ABC", "Mateo Diaz", "mateo@gmail.com", "3009876543", log)
    except DatosInvalidosError as e:
        print("Error controlado ->", e)
