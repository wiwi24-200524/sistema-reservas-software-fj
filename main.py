from entidades import Cliente
from excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    ErrorSistemaFJ,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from logger import RegistradorLogs
from reserva import Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


def ejecutar_operacion(
    numero: int,
    descripcion: str,
    accion,
    registrador: RegistradorLogs,
) -> bool:
    """Ejecuta una operación simulada con try/except/else/finally sin detener el flujo."""
    print(f"\n--- Operación #{numero}: {descripcion} ---")
    exito = False
    try:
        resultado = accion()
    except ErrorSistemaFJ as exc:
        registrador.registrar_evento(
            "ERROR",
            f"[OP #{numero} FALLIDA] {descripcion} | {type(exc).__name__}: {exc}",
        )
        print(f"[ERROR CONTROLADO] {exc}")
    except (ValueError, TypeError, AttributeError) as exc:
        registrador.registrar_evento(
            "ERROR",
            f"[OP #{numero} ERROR INESPERADO] {descripcion} | {type(exc).__name__}: {exc}",
        )
        print(f"[ERROR INESPERADO CONTROLADO] {exc}")
    else:
        exito = True
        registrador.registrar_evento("INFO", f"[OP #{numero} EXITOSA] {descripcion}")
        if resultado is not None:
            print(f"[OK] {resultado}")
    finally:
        estado_op = "EXITOSA" if exito else "CON ERROR CONTROLADO"
        print(f"[FIN OP #{numero}] Estado: {estado_op}")
    return exito


def main() -> None:
    registrador = RegistradorLogs()
    clientes: list[Cliente] = []
    servicios = []
    reservas: list[Reserva] = []

    registrador.registrar_evento("INFO", "=== Inicio de simulación Software FJ ===")

    # 1. Crear y validar cliente válido #1 (documento numérico de >= 6 dígitos)
    def op1():
        cliente = Cliente(
            "1095823401",
            "Laura Gómez",
            "laura.gomez@gmail.com",
            "3134156780",
            registrador,
        )
        if not cliente.validar():
            raise DatosInvalidosError("La validación del cliente #1 no fue exitosa.")
        clientes.append(cliente)
        return f"Cliente registrado: {cliente.obtener_info()}"

    ejecutar_operacion(1, "Registro válido de cliente #1", op1, registrador)

    # 2. Crear y validar cliente válido #2
    def op2():
        cliente = Cliente(
            "1095823402",
            "Andrés Pérez",
            "andres.perez@gmail.com",
            "3014659090",
            registrador,
        )
        if not cliente.validar():
            raise DatosInvalidosError("La validación del cliente #2 no fue exitosa.")
        clientes.append(cliente)
        return f"Cliente registrado: {cliente.obtener_info()}"

    ejecutar_operacion(2, "Registro válido de cliente #2", op2, registrador)

    # 3. Intento inválido de registro de cliente (encadenamiento de excepciones)
    def op3():
        try:
            cliente_malo = Cliente("12A", "A", "correo_sin_arroba", "12", registrador)
            cliente_malo.validar()
        except DatosInvalidosError as exc:
            raise DatosInvalidosError(
                "No se pudo registrar el cliente por datos incompletos o inválidos."
            ) from exc

    ejecutar_operacion(3, "Registro inválido de cliente (encadenamiento)", op3, registrador)

    # 4. Crear servicios válidos (Sala, Equipo y Asesoría)
    def op4():
        sala = ReservaSala("SAL-101", "Sala de Juntas Norte", 80.0, capacidad_personas=12)
        equipo = AlquilerEquipo(
            "EQP-201", "Laptops Desarrollador", 45.0, cantidad_unidades=3
        )
        asesoria = AsesoriaEspecializada(
            "ASE-301",
            "Arquitectura de Software",
            120.0,
            especialidad="Cloud y Microservicios",
        )
        sala.validar()
        equipo.validar()
        asesoria.validar()
        servicios.extend([sala, equipo, asesoria])
        return f"Se registraron {len(servicios)} servicios válidos."

    ejecutar_operacion(4, "Creación y validación de 3 servicios especializados", op4, registrador)

    # 5. Intento inválido de creación de servicio (tarifa negativa con encadenamiento)
    def op5():
        try:
            servicio_malo = ReservaSala("SAL-999", "Sala Error", -50.0, capacidad_personas=5)
            servicio_malo.validar()
        except DatosInvalidosError as exc:
            raise CalculoInconsistenteError(
                "Error al configurar servicio con tarifa base inválida."
            ) from exc

    ejecutar_operacion(5, "Creación inválida de servicio (tarifa negativa)", op5, registrador)

    # 6. Cálculo de costo con parámetros opcionales (descuento, impuesto y recargo)
    def op6():
        if not servicios:
            raise ServicioNoDisponibleError("No hay servicios disponibles para cotizar.")
        equipo = servicios[1]
        costo_con_ajustes = equipo.calcular_costo(
            duracion=2,
            descuento_pct=10.0,
            impuesto_pct=19.0,
            recargo_mantenimiento=15.0,
        )
        return (
            f"Costo cotizado para {equipo.codigo} "
            f"(2 periodos, desc 10%, IVA 19%, recargo $15): ${costo_con_ajustes:.2f}"
        )

    ejecutar_operacion(6, "Cálculo de costo con descuento, impuesto y recargo", op6, registrador)

    # 7. Reserva exitosa #1 (Sala para Cliente #1)
    def op7():
        if not clientes or not servicios:
            raise ReservaInvalidaError("Faltan clientes o servicios para crear la reserva.")
        reserva = Reserva(
            codigo_reserva="RES-001",
            cliente=clientes[0],
            servicio=servicios[0],
            duracion=3,
            registrador=registrador,
            descuento_pct=5.0,
            impuesto_pct=19.0,
        )
        resumen = reserva.procesar()
        reservas.append(reserva)
        return resumen

    ejecutar_operacion(7, "Reserva exitosa #1 (Sala)", op7, registrador)

    # 8. Reserva exitosa #2 (Asesoría para Cliente #2)
    def op8():
        if len(clientes) < 2 or len(servicios) < 3:
            raise ReservaInvalidaError("No hay suficientes clientes o servicios para la reserva.")
        reserva = Reserva(
            codigo_reserva="RES-002",
            cliente=clientes[1],
            servicio=servicios[2],
            duracion=2,
            registrador=registrador,
            impuesto_pct=19.0,
        )
        resumen = reserva.procesar()
        reservas.append(reserva)
        return resumen

    ejecutar_operacion(8, "Reserva exitosa #2 (Asesoría)", op8, registrador)

    # 9. Reserva fallida por servicio no disponible
    def op9():
        if not clientes or len(servicios) < 2:
            raise ReservaInvalidaError("Datos insuficientes para probar servicio no disponible.")
        equipo = servicios[1]
        equipo.disponible = False
        try:
            reserva_fallida = Reserva(
                codigo_reserva="RES-003",
                cliente=clientes[0],
                servicio=equipo,
                duracion=1,
                registrador=registrador,
            )
            reserva_fallida.confirmar()
        finally:
            equipo.disponible = True

    ejecutar_operacion(9, "Reserva fallida por servicio no disponible", op9, registrador)

    # 10. Intento inválido de reconfirmar una reserva ya confirmada
    def op10():
        if not reservas:
            raise ReservaInvalidaError("No existen reservas previas para reconfirmar.")
        reservas[0].confirmar()

    ejecutar_operacion(10, "Intento inválido de confirmar reserva ya confirmada", op10, registrador)

    # 11. Cancelación válida de una reserva confirmada
    def op11():
        if len(reservas) < 2:
            raise ReservaInvalidaError("No hay segunda reserva para cancelar.")
        reservas[1].cancelar("Reprogramación solicitada por el cliente")
        return f"Estado actual de {reservas[1].codigo_reserva}: {reservas[1].estado}"

    ejecutar_operacion(11, "Cancelación válida de reserva #2", op11, registrador)

    # 12. Intento inválido de procesar una reserva cancelada
    def op12():
        if len(reservas) < 2:
            raise ReservaInvalidaError("No hay reserva cancelada para probar.")
        reservas[1].procesar()

    ejecutar_operacion(12, "Intento inválido de procesar reserva cancelada", op12, registrador)

    registrador.registrar_evento(
        "INFO",
        f"=== Fin de simulación Software FJ | Clientes: {len(clientes)} | "
        f"Servicios: {len(servicios)} | Reservas: {len(reservas)} ===",
    )

    print("\n================ RESUMEN FINAL EN MEMORIA ================")
    print(f"Total clientes válidos: {len(clientes)}")
    print(f"Total servicios registrados: {len(servicios)}")
    print(f"Total reservas creadas: {len(reservas)}")
    for r in reservas:
        costo_str = f"${r.costo_total:.2f}" if r.costo_total is not None else "N/A"
        print(f"  - {r.codigo_reserva}: estado='{r.estado}', costo={costo_str}")


if __name__ == "__main__":
    main()