
"""
Sistema Integral de Gestion de Clientes, Servicios y Reservas
Empresa: Software FJ
Curso: Programacion - UNAD
Fase 4: Practicas simuladas

Este programa aplica programacion orientada a objetos,
validaciones y manejo de excepciones.
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging


# ==========================================================
# 1. CONFIGURACION DEL SISTEMA DE REGISTRO (LOGS)
# ==========================================================

# Configuracion para guardar eventos y errores en un archivo.
logging.basicConfig(
    filename="sistema.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# ==========================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ==========================================================

class ErrorSistema(Exception):
    """Excepcion base del sistema Software FJ."""
    pass


class DatosInvalidosError(ErrorSistema):
    """Error cuando los datos ingresados no son validos."""
    pass


class ServicioNoDisponibleError(ErrorSistema):
    """Error cuando un servicio no se encuentra disponible."""
    pass


class ReservaInvalidaError(ErrorSistema):
    """Error cuando una reserva no puede realizarse."""
    pass


# ==========================================================
# 3. CLASE ABSTRACTA ENTIDAD
# ==========================================================

class Entidad(ABC):
    """Clase abstracta que representa una entidad general."""

    def __init__(self, identificador):
        if not identificador:
            raise DatosInvalidosError("El identificador es obligatorio.")
        self._identificador = identificador

    @property
    def identificador(self):
        """Permite consultar el identificador de forma controlada."""
        return self._identificador

    @abstractmethod
    def mostrar_informacion(self):
        """Metodo que deben implementar las clases derivadas."""
        pass


# ==========================================================
# 4. CLASE CLIENTE
# ==========================================================

class Cliente(Entidad):
    """Representa un cliente de Software FJ."""

    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)

        # Validacion del nombre.
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidosError("El nombre del cliente es obligatorio.")

        # Validacion basica del correo.
        if not isinstance(correo, str) or "@" not in correo:
            raise DatosInvalidosError("El correo electronico no es valido.")

        # Validacion del telefono.
        if not str(telefono).isdigit() or len(str(telefono)) < 7:
            raise DatosInvalidosError("El telefono debe contener minimo 7 digitos.")

        # Encapsulacion de los datos.
        self.__nombre = nombre.strip()
        self.__correo = correo.strip()
        self.__telefono = str(telefono)

    @property
    def nombre(self):
        return self.__nombre

    def mostrar_informacion(self):
        return (
            f"Cliente: {self.__nombre} | "
            f"Correo: {self.__correo} | "
            f"Telefono: {self.__telefono}"
        )


# ==========================================================
# 5. CLASE ABSTRACTA SERVICIO
# ==========================================================

class Servicio(Entidad, ABC):
    """Clase abstracta para los servicios ofrecidos."""

    def __init__(self, identificador, nombre, tarifa_base):
        super().__init__(identificador)

        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise DatosInvalidosError("La tarifa debe ser mayor a cero.")

        self._nombre = nombre
        self._tarifa_base = float(tarifa_base)

    @abstractmethod
    def calcular_costo(self, duracion):
        """Calcula el costo segun el tipo de servicio."""
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        """Valida los parametros necesarios del servicio."""
        pass

    def mostrar_informacion(self):
        return f"Servicio: {self._nombre} | Tarifa: ${self._tarifa_base:,.0f}"


# ==========================================================
# 6. SERVICIO DE RESERVA DE SALAS
# ==========================================================

class ReservaSala(Servicio):
    """Servicio para reservar salas de reuniones."""

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duracion de la sala debe ser positiva.")

    def calcular_costo(self, duracion, impuesto=0):
        """Calcula el costo con opcion de aplicar porcentaje de impuesto."""
        self.validar_parametros(duracion)

        if not isinstance(impuesto, (int, float)) or impuesto < 0:
            raise DatosInvalidosError("El impuesto no puede ser negativo.")

        subtotal = self._tarifa_base * duracion
        return subtotal + (subtotal * impuesto / 100)


# ==========================================================
# 7. SERVICIO DE ALQUILER DE EQUIPOS
# ==========================================================

class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos tecnologicos."""

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duracion del alquiler debe ser positiva.")

    def calcular_costo(self, duracion, descuento=0):
        """Calcula el costo aplicando un descuento opcional."""
        self.validar_parametros(duracion)

        if not isinstance(descuento, (int, float)) or not 0 <= descuento <= 100:
            raise DatosInvalidosError("El descuento debe estar entre 0 y 100.")

        subtotal = self._tarifa_base * duracion
        return subtotal - (subtotal * descuento / 100)


# ==========================================================
# 8. SERVICIO DE ASESORIAS ESPECIALIZADAS
# ==========================================================

class Asesoria(Servicio):
    """Servicio de asesoria profesional especializada."""

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duracion de la asesoria debe ser positiva.")

    def calcular_costo(self, duracion):
        """Calcula el costo de la asesoria segun su duracion."""
        self.validar_parametros(duracion)
        return self._tarifa_base * duracion


# ==========================================================
# 9. CLASE RESERVA
# ==========================================================

class Reserva(Entidad):
    """Gestiona una reserva de un cliente para un servicio."""

    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)

        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("Debe asociarse un cliente valido.")

        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("Debe asociarse un servicio valido.")

        servicio.validar_parametros(duracion)

        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = "Pendiente"
        self._costo = servicio.calcular_costo(duracion)

    @property
    def estado(self):
        return self._estado

    def confirmar(self):
        """Confirma una reserva que se encuentre pendiente."""
        if self._estado != "Pendiente":
            raise ReservaInvalidaError(
                "Solo se pueden confirmar reservas pendientes."
            )

        self._estado = "Confirmada"
        logging.info("Reserva %s confirmada.", self.identificador)

    def cancelar(self):
        """Cancela una reserva que no haya sido cancelada previamente."""
        if self._estado == "Cancelada":
            raise ReservaInvalidaError("La reserva ya se encuentra cancelada.")

        self._estado = "Cancelada"
        logging.info("Reserva %s cancelada.", self.identificador)

    def procesar(self):
        """Procesa una reserva y registra los errores que se presenten."""
        try:
            if self._estado == "Cancelada":
                raise ReservaInvalidaError(
                    "No se puede procesar una reserva cancelada."
                )

            self.confirmar()
            print(f"Reserva {self.identificador} procesada correctamente.")

        except ReservaInvalidaError as error:
            logging.error("Error procesando reserva: %s", error)
            raise

        else:
            print("Proceso finalizado sin errores.")

        finally:
            print(f"Finalizando proceso de reserva {self.identificador}.")

    def mostrar_informacion(self):
        return (
            f"Reserva: {self.identificador} | "
            f"Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio._nombre} | "
            f"Duracion: {self._duracion} | "
            f"Costo: ${self._costo:,.0f} | "
            f"Estado: {self._estado}"
        )


# ==========================================================
# 10. SISTEMA INTEGRAL DE GESTION
# ==========================================================

class SistemaSoftwareFJ:
    """Administra clientes, servicios y reservas mediante listas."""

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El objeto no corresponde a un cliente.")

        if any(c.identificador == cliente.identificador for c in self.clientes):
            raise DatosInvalidosError("El cliente ya se encuentra registrado.")

        self.clientes.append(cliente)
        logging.info("Cliente registrado: %s", cliente.identificador)
        print("Cliente registrado correctamente.")

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El objeto no corresponde a un servicio.")

        if any(s.identificador == servicio.identificador for s in self.servicios):
            raise DatosInvalidosError("El servicio ya se encuentra registrado.")

        self.servicios.append(servicio)
        logging.info("Servicio registrado: %s", servicio.identificador)
        print("Servicio registrado correctamente.")

    def crear_reserva(self, reserva):
        if not isinstance(reserva, Reserva):
            raise ReservaInvalidaError("El objeto no corresponde a una reserva.")

        if any(r.identificador == reserva.identificador for r in self.reservas):
            raise ReservaInvalidaError("El identificador de reserva ya existe.")

        self.reservas.append(reserva)
        logging.info("Reserva creada: %s", reserva.identificador)
        print("Reserva creada correctamente.")

    def mostrar_clientes(self):
        print("\n--- LISTADO DE CLIENTES ---")
        for cliente in self.clientes:
            print(cliente.mostrar_informacion())

    def mostrar_servicios(self):
        print("\n--- LISTADO DE SERVICIOS ---")
        for servicio in self.servicios:
            print(servicio.mostrar_informacion())

    def mostrar_reservas(self):
        print("\n--- LISTADO DE RESERVAS ---")
        for reserva in self.reservas:
            print(reserva.mostrar_informacion())


# ==========================================================
# 11. SIMULACION DE OPERACIONES (MINIMO 10)
# ==========================================================

def ejecutar_simulacion():
    """Ejecuta operaciones validas e invalidas para comprobar el sistema."""

    sistema = SistemaSoftwareFJ()

    print("=" * 60)
    print(" SISTEMA INTEGRAL DE GESTION - SOFTWARE FJ")
    print("=" * 60)

    # Operacion 1: Registro de cliente valido.
    try:
        cliente1 = Cliente("C001", "Carlos Perez", "carlos@email.com", "3001234567")
        sistema.registrar_cliente(cliente1)
    except ErrorSistema as error:
        logging.error("Operacion 1: %s", error)
        print("Error:", error)

    # Operacion 2: Registro de otro cliente valido.
    try:
        cliente2 = Cliente("C002", "Laura Gomez", "laura@email.com", "3101234567")
        sistema.registrar_cliente(cliente2)
    except ErrorSistema as error:
        logging.error("Operacion 2: %s", error)
        print("Error:", error)

    # Operacion 3: Intento de registro con correo invalido.
    try:
        cliente_invalido = Cliente("C003", "Pedro Ruiz", "correo_invalido", "3201234567")
        sistema.registrar_cliente(cliente_invalido)
    except ErrorSistema as error:
        logging.error("Operacion 3: %s", error)
        print("Operacion 3 controlada: %s" % error)

    # Operacion 4: Creacion de servicio de salas.
    try:
        sala = ReservaSala("S001", "Reserva de sala", 80000)
        sistema.registrar_servicio(sala)
    except ErrorSistema as error:
        logging.error("Operacion 4: %s", error)
        print("Error:", error)

    # Operacion 5: Creacion de servicio de alquiler de equipos.
    try:
        equipo = AlquilerEquipo("S002", "Alquiler de equipos", 50000)
        sistema.registrar_servicio(equipo)
    except ErrorSistema as error:
        logging.error("Operacion 5: %s", error)
        print("Error:", error)

    # Operacion 6: Creacion de servicio de asesoria.
    try:
        asesoria = Asesoria("S003", "Asesoria especializada", 120000)
        sistema.registrar_servicio(asesoria)
    except ErrorSistema as error:
        logging.error("Operacion 6: %s", error)
        print("Error:", error)

    # Operacion 7: Intento de crear servicio con tarifa negativa.
    try:
        servicio_invalido = ReservaSala("S004", "Sala invalida", -1000)
        sistema.registrar_servicio(servicio_invalido)
    except ErrorSistema as error:
        logging.error("Operacion 7: %s", error)
        print("Operacion 7 controlada: %s" % error)

    # Operacion 8: Creacion de reserva valida.
    try:
        reserva1 = Reserva("R001", cliente1, sala, 2)
        sistema.crear_reserva(reserva1)
    except ErrorSistema as error:
        logging.error("Operacion 8: %s", error)
        print("Error:", error)

    # Operacion 9: Confirmacion de reserva.
    try:
        reserva1.confirmar()
        print("Operacion 9: Reserva confirmada.")
    except ErrorSistema as error:
        logging.error("Operacion 9: %s", error)
        print("Error:", error)

    # Operacion 10: Intento de confirmar reserva ya confirmada.
    try:
        reserva1.confirmar()
    except ErrorSistema as error:
        logging.error("Operacion 10: %s", error)
        print("Operacion 10 controlada: %s" % error)

    # Operacion 11: Reserva con duracion invalida.
    try:
        reserva_invalida = Reserva("R002", cliente2, equipo, 0)
        sistema.crear_reserva(reserva_invalida)
    except ErrorSistema as error:
        logging.error("Operacion 11: %s", error)
        print("Operacion 11 controlada: %s" % error)

    # Operacion 12: Cancelacion de reserva.
    try:
        reserva1.cancelar()
        print("Operacion 12: Reserva cancelada.")
    except ErrorSistema as error:
        logging.error("Operacion 12: %s", error)
        print("Error:", error)

    # Operacion 13: Intento de procesar reserva cancelada.
    try:
        reserva1.procesar()
    except ErrorSistema as error:
        logging.error("Operacion 13: %s", error)
        print("Operacion 13 controlada: %s" % error)

    # Operacion 14: Calculo de sala con impuesto.
    try:
        costo_sala = sala.calcular_costo(2, impuesto=19)
        print(f"Operacion 14: Costo sala con impuesto: ${costo_sala:,.0f}")
    except ErrorSistema as error:
        logging.error("Operacion 14: %s", error)
        print("Error:", error)

    # Operacion 15: Calculo de equipo con descuento.
    try:
        costo_equipo = equipo.calcular_costo(3, descuento=10)
        print(f"Operacion 15: Costo equipo con descuento: ${costo_equipo:,.0f}")
    except ErrorSistema as error:
        logging.error("Operacion 15: %s", error)
        print("Error:", error)

    # Operacion 16: Encadenamiento de excepciones.
    try:
        try:
            int("dato_no_numerico")
        except ValueError as error_original:
            raise DatosInvalidosError(
                "No fue posible convertir el dato ingresado."
            ) from error_original
    except DatosInvalidosError as error:
        logging.exception("Operacion 16: Excepcion encadenada.")
        print("Operacion 16 controlada: %s" % error)

    # Mostrar informacion final.
    sistema.mostrar_clientes()
    sistema.mostrar_servicios()
    sistema.mostrar_reservas()

    print("\nSimulacion finalizada.")
    print("Los eventos y errores se registran en sistema.log.")


# ==========================================================
# 12. PUNTO DE ENTRADA DEL PROGRAMA
# ==========================================================

if __name__ == "__main__":
    try:
        ejecutar_simulacion()
    except Exception as error:
        logging.exception("Error inesperado en la ejecucion principal.")
        print("Se presento un error inesperado:", error)
    finally:
        print("Aplicacion Software FJ finalizada.")
