from datetime import datetime
from entidades import Cliente
from excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    ErrorSistemaFJ,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from logger import RegistradorLogs
from servicios import Servicio


class Reserva:
    """Gestiona una reserva de servicio para un cliente de Software FJ."""

    ESTADOS_VALIDOS = ("pendiente", "confirmada", "cancelada")

    def __init__(
        self,
        codigo_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        registrador: RegistradorLogs | None = None,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> None:
        self._registrador = registrador if registrador is not None else RegistradorLogs()

        if not isinstance(codigo_reserva, str) or not codigo_reserva.strip():
            raise DatosInvalidosError("El código de reserva debe ser un texto no vacío.")
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere una instancia válida de Servicio.")
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duración de la reserva debe ser mayor que cero.")

        self._codigo_reserva = codigo_reserva.strip()
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = float(duracion)
        self._descuento_pct = descuento_pct
        self._impuesto_pct = impuesto_pct
        self._estado = "pendiente"
        self._fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._costo_total: float | None = None

        self._registrador.registrar_evento(
            "INFO",
            f"Reserva '{self._codigo_reserva}' creada en estado '{self._estado}' "
            f"para cliente '{self._cliente.obtener_info()}' y servicio '{self._servicio.codigo}'.",
        )

    @property
    def codigo_reserva(self) -> str:
        return self._codigo_reserva

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion(self) -> float:
        return self._duracion

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float | None:
        return self._costo_total

    def _calcular_monto_reserva(self) -> float:
        """Calcula y valida el costo de la reserva encadenando errores si fallan."""
        try:
            monto = self._servicio.calcular_costo(
                self._duracion,
                descuento_pct=self._descuento_pct,
                impuesto_pct=self._impuesto_pct,
            )
        except CalculoInconsistenteError:
            raise
        except DatosInvalidosError as exc:
            raise CalculoInconsistenteError(
                f"Parámetros inválidos al calcular el costo de '{self._codigo_reserva}'."
            ) from exc
        except Exception as exc:
            raise CalculoInconsistenteError(
                f"Error inesperado calculando el costo de '{self._codigo_reserva}'."
            ) from exc

        if monto <= 0:
            raise CalculoInconsistenteError(
                f"El monto calculado para '{self._codigo_reserva}' no es válido: {monto}."
            )
        return monto

    def confirmar(self) -> None:
        """Valida cliente, servicio y costo para pasar la reserva a 'confirmada'."""
        operacion_exitosa = False
        try:
            if self._estado == "cancelada":
                raise ReservaInvalidaError(
                    f"No se puede confirmar la reserva '{self._codigo_reserva}' porque está cancelada."
                )
            if self._estado == "confirmada":
                raise ReservaInvalidaError(
                    f"La reserva '{self._codigo_reserva}' ya se encuentra confirmada."
                )

            if not self._cliente.validar():
                raise DatosInvalidosError(
                    f"El cliente asociado a '{self._codigo_reserva}' no es válido."
                )
            self._servicio.validar()
            self._costo_total = self._calcular_monto_reserva()
        except (DatosInvalidosError, ServicioNoDisponibleError, CalculoInconsistenteError) as exc:
            self._registrador.registrar_evento(
                "ERROR",
                f"Fallo al confirmar reserva '{self._codigo_reserva}': {exc}",
            )
            raise ReservaInvalidaError(
                f"Fallo al confirmar la reserva '{self._codigo_reserva}'."
            ) from exc
        except ErrorSistemaFJ as exc:
            self._registrador.registrar_evento(
                "ERROR",
                f"Error del sistema en reserva '{self._codigo_reserva}': {exc}",
            )
            raise
        else:
            self._estado = "confirmada"
            operacion_exitosa = True
            self._registrador.registrar_evento(
                "INFO",
                f"Reserva '{self._codigo_reserva}' CONFIRMADA. Total: ${self._costo_total:.2f}.",
            )
        finally:
            if not operacion_exitosa:
                self._registrador.registrar_evento(
                    "INFO",
                    f"Intento de confirmación finalizado sin éxito para '{self._codigo_reserva}' "
                    f"(estado actual: '{self._estado}').",
                )

    def cancelar(self, motivo: str = "Cancelada por solicitud del usuario") -> None:
        """Cancela una reserva activa/pendiente si aún no está cancelada."""
        try:
            if self._estado == "cancelada":
                raise ReservaInvalidaError(
                    f"La reserva '{self._codigo_reserva}' ya estaba cancelada."
                )
            motivo_limpio = (
                motivo.strip()
                if isinstance(motivo, str) and motivo.strip()
                else "Sin motivo especificado"
            )
        except ReservaInvalidaError as exc:
            self._registrador.registrar_evento(
                "ERROR",
                f"Fallo al cancelar reserva '{self._codigo_reserva}': {exc}",
            )
            raise
        else:
            self._estado = "cancelada"
            self._registrador.registrar_evento(
                "INFO",
                f"Reserva '{self._codigo_reserva}' CANCELADA. Motivo: {motivo_limpio}.",
            )
        finally:
            self._registrador.registrar_evento(
                "INFO",
                f"Revisión de cancelación completada para '{self._codigo_reserva}'.",
            )

    def procesar(self) -> str:
        """Procesa la reserva según su estado y devuelve un resumen legible."""
        try:
            if self._estado == "pendiente":
                self.confirmar()
            elif self._estado == "cancelada":
                raise ReservaInvalidaError(
                    f"No se puede procesar la reserva '{self._codigo_reserva}' porque está cancelada."
                )

            if self._costo_total is None:
                self._costo_total = self._calcular_monto_reserva()
        except ErrorSistemaFJ as exc:
            self._registrador.registrar_evento(
                "ERROR",
                f"Fallo al procesar reserva '{self._codigo_reserva}': {exc}",
            )
            raise ReservaInvalidaError(
                f"No fue posible procesar la reserva '{self._codigo_reserva}'."
            ) from exc
        else:
            resumen = (
                f"Reserva {self._codigo_reserva} | Estado: {self._estado} | "
                f"Cliente: {self._cliente.obtener_info()} | "
                f"Servicio: {self._servicio.obtener_info()} | "
                f"Duración: {self._duracion} | Total: ${self._costo_total:.2f}"
            )
            self._registrador.registrar_evento(
                "INFO",
                f"Reserva '{self._codigo_reserva}' procesada correctamente.",
            )
            return resumen