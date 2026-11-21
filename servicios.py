from abc import ABC, abstractmethod
from entidades import EntidadSistema
from excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    ServicioNoDisponibleError,
)


class Servicio(EntidadSistema, ABC):
    """Clase abstracta base para los servicios ofrecidos por el sistema."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_entidad=codigo)  # Llama explícitamente al constructor de EntidadSistema usando el código como id_entidad
        # Validamos parámetros iniciales antes de asignar atributos internos.
        self._codigo = self._validar_texto_no_vacio(codigo, "código del servicio")
        self._nombre = self._validar_texto_no_vacio(nombre, "nombre del servicio")
        self._tarifa_base = self._validar_monto_positivo(tarifa_base, "tarifa base")
        self._disponible = bool(disponible)

    @staticmethod
    def _validar_texto_no_vacio(valor: str, campo: str) -> str:
        """Verifica que un texto obligatorio sea string no vacío."""
        if not isinstance(valor, str) or not valor.strip():
            raise DatosInvalidosError(f"El {campo} debe ser un texto no vacío.")
        return valor.strip()

    @staticmethod
    def _validar_monto_positivo(valor: float, campo: str) -> float:
        """Verifica que un valor numérico sea positivo y finito."""
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise DatosInvalidosError(f"El {campo} debe ser un valor numérico.")
        monto = float(valor)
        if monto <= 0:
            raise DatosInvalidosError(f"El {campo} debe ser mayor que cero.")
        return monto

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        if not isinstance(estado, bool):
            raise DatosInvalidosError("La disponibilidad debe ser un valor booleano.")
        self._disponible = estado

    def validar(self) -> bool:
        """Valida el estado general del servicio y su disponibilidad."""
        self._validar_texto_no_vacio(self._codigo, "código del servicio")
        self._validar_texto_no_vacio(self._nombre, "nombre del servicio")
        self._validar_monto_positivo(self._tarifa_base, "tarifa base")
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._nombre}' ({self._codigo}) no está disponible."
            )
        return True

    @abstractmethod
    def calcular_costo(
        self,
        duracion: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> float:
        """Calcula el costo total según duración y parámetros opcionales."""

    def _aplicar_ajustes_financieros(
        self, subtotal: float, descuento_pct: float, impuesto_pct: float
    ) -> float:
        """Aplica descuento e impuesto validando que el resultado sea consistente."""
        if subtotal <= 0:
            raise CalculoInconsistenteError(
                "El subtotal calculado no puede ser menor o igual a cero."
            )
        if not isinstance(descuento_pct, (int, float)) or not (0 <= descuento_pct < 100):
            raise DatosInvalidosError(
                "El porcentaje de descuento debe estar entre 0 y 99.99."
            )
        if not isinstance(impuesto_pct, (int, float)) or not (0 <= impuesto_pct <= 100):
            raise DatosInvalidosError(
                "El porcentaje de impuesto debe estar entre 0 y 100."
            )

        # Primero aplicamos descuento y luego el impuesto sobre el valor con descuento.
        con_descuento = subtotal * (1 - float(descuento_pct) / 100.0)
        total = con_descuento * (1 + float(impuesto_pct) / 100.0)

        if total <= 0:
            raise CalculoInconsistenteError(
                "El costo final calculado es inconsistente (menor o igual a cero)."
            )
        return round(total, 2)


class ReservaSala(Servicio):
    """Servicio especializado para reserva de salas (costo por horas)."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        capacidad_personas: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(codigo, nombre, tarifa_base, disponible)
        if isinstance(capacidad_personas, bool) or not isinstance(capacidad_personas, int) or capacidad_personas <= 0:
            raise DatosInvalidosError(
                "La capacidad de la sala debe ser un entero mayor que cero."
            )
        self._capacidad_personas = capacidad_personas

    @property
    def capacidad_personas(self) -> int:
        return self._capacidad_personas

    def calcular_costo(
        self,
        duracion: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> float:
        """Calcula costo por horas de sala con descuento e impuesto opcionales."""
        horas = self._validar_monto_positivo(duracion, "duración en horas")
        subtotal = self._tarifa_base * horas
        return self._aplicar_ajustes_financieros(subtotal, descuento_pct, impuesto_pct)

    def obtener_info(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"[Sala] {self._codigo} - {self._nombre} | "
            f"Capacidad: {self._capacidad_personas} personas | "
            f"Tarifa/hora: ${self._tarifa_base:.2f} | {estado}"
        )


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de equipos tecnológicos."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        cantidad_unidades: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(codigo, nombre, tarifa_base, disponible)
        if isinstance(cantidad_unidades, bool) or not isinstance(cantidad_unidades, int) or cantidad_unidades <= 0:
            raise DatosInvalidosError(
                "La cantidad de unidades del equipo debe ser un entero mayor que cero."
            )
        self._cantidad_unidades = cantidad_unidades

    @property
    def cantidad_unidades(self) -> int:
        return self._cantidad_unidades

    def calcular_costo(
        self,
        duracion: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        recargo_mantenimiento: float = 0.0,
    ) -> float:
        """Calcula costo por días/horas de alquiler, unidades y recargo opcional."""
        periodos = self._validar_monto_positivo(duracion, "duración del alquiler")
        if isinstance(recargo_mantenimiento, bool) or not isinstance(
            recargo_mantenimiento, (int, float)
        ) or recargo_mantenimiento < 0:
            raise DatosInvalidosError(
                "El recargo de mantenimiento no puede ser negativo."
            )
        subtotal = (self._tarifa_base * periodos * self._cantidad_unidades) + float(
            recargo_mantenimiento
        )
        return self._aplicar_ajustes_financieros(subtotal, descuento_pct, impuesto_pct)

    def obtener_info(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"[Equipo] {self._codigo} - {self._nombre} | "
            f"Unidades: {self._cantidad_unidades} | "
            f"Tarifa/unidad/periodo: ${self._tarifa_base:.2f} | {estado}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para asesorías técnicas o de arquitectura."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        especialidad: str,
        disponible: bool = True,
    ) -> None:
        super().__init__(codigo, nombre, tarifa_base, disponible)
        self._especialidad = self._validar_texto_no_vacio(
            especialidad, "especialidad de la asesoría"
        )

    @property
    def especialidad(self) -> str:
        return self._especialidad

    def calcular_costo(
        self,
        duracion: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> float:
        """Calcula costo por sesiones/horas de asesoría con descuento e impuesto."""
        sesiones_o_horas = self._validar_monto_positivo(
            duracion, "duración de la asesoría"
        )
        subtotal = self._tarifa_base * sesiones_o_horas
        return self._aplicar_ajustes_financieros(subtotal, descuento_pct, impuesto_pct)

    def obtener_info(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"[Asesoría] {self._codigo} - {self._nombre} | "
            f"Especialidad: {self._especialidad} | "
            f"Tarifa base: ${self._tarifa_base:.2f} | {estado}"
        )