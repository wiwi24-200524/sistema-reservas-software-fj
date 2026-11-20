# excepciones.py

# Excepción general para los errores de Software FJ
class ErrorSistemaFJ(Exception):
    pass

# Cuando ingresan datos vacíos, negativos o con mal formato
class DatosInvalidosError(ErrorSistemaFJ):
    pass

# Cuando un servicio está inactivo o no hay disponibilidad
class ServicioNoDisponibleError(ErrorSistemaFJ):
    pass

# Cuando falla algo al crear, confirmar o cancelar una reserva
class ReservaInvalidaError(ErrorSistemaFJ):
    pass

# Cuando hay algún error calculando precios, impuestos o descuentos
class CalculoInconsistenteError(ErrorSistemaFJ):
    pass

