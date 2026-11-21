"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas.
Empresa: Software FJ
Curso: Programación (213023) - UNAD
Fase 4: Prácticas simuladas

Implementa POO (abstracción, herencia, polimorfismo y encapsulación),
validaciones estrictas, manejo avanzado de excepciones y registro en logs
en memoria (listas) sin utilizar bases de datos.
"""

from abc import ABC, abstractmethod  # Importa herramientas para clases y métodos abstractos.
import logging  # Importa logging para registrar eventos y errores en archivo.


# ==========================================================
# 1. CONFIGURACIÓN DEL SISTEMA DE REGISTRO (LOGS)
# ==========================================================
logging.basicConfig(
    filename="sistema.log",  # Archivo de texto donde se guardarán eventos y errores.
    level=logging.INFO,  # Registra mensajes desde nivel INFO en adelante.
    format="%(asctime)s - %(levelname)s - %(message)s",  # Incluye fecha/hora, nivel y detalle.
    encoding="utf-8",  # Codificación UTF-8 para tildes y caracteres en español.
)


# ==========================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ==========================================================
class ErrorSistema(Exception):
    """Excepción base de la aplicación Software FJ."""
    pass


class DatosInvalidosError(ErrorSistema):
    """Error cuando algún dato o parámetro no cumple con las reglas esperadas."""
    pass


class ServicioNoDisponibleError(ErrorSistema):
    """Error cuando se intenta usar o reservar un servicio no disponible."""
    pass


class ReservaInvalidaError(ErrorSistema):
    """Error cuando una operación sobre una reserva no es válida o no procede."""
    pass


# ==========================================================
# 3. CLASE ABSTRACTA ENTIDAD
# ==========================================================
class Entidad(ABC):
    """Clase abstracta que representa una entidad general del sistema."""

    def __init__(self, identificador):
        # Verifica que el identificador no esté vacío ni compuesto solo por espacios.
        if not identificador or not str(identificador).strip():
            raise DatosInvalidosError("El identificador es obligatorio.")
        self._identificador = str(identificador).strip()  # Atributo protegido de identificación.

    @property
    def identificador(self):
        """Permite consultar el identificador de forma controlada."""
        return self._identificador

    @abstractmethod
    def mostrar_informacion(self):
        """Método abstracto que cada clase hija debe implementar."""
        pass


# ==========================================================
# 4. CLASE CLIENTE
# ==========================================================
class Cliente(Entidad):
    """Representa a un cliente con encapsulación de datos personales y validaciones."""

    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)  # Valida y asigna el identificador en Entidad.

        # Valida que el nombre sea texto no vacío.
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidosError("El nombre del cliente es obligatorio.")

        # Valida estructura mínima de correo electrónico.
        if not isinstance(correo, str) or "@" not in correo or "." not in correo.split("@")[-1]:
            raise DatosInvalidosError("El correo electrónico no es válido.")

        telefono_limpio = str(telefono).strip()  # Normaliza el teléfono como texto.
        # Exige que tenga solo dígitos y al menos 7 caracteres.
        if not telefono_limpio.isdigit() or len(telefono_limpio) < 7:
            raise DatosInvalidosError("El teléfono debe contener mínimo 7 dígitos.")

        # Encapsulación con atributos privados (__).
        self.__nombre = nombre.strip()
        self.__correo = correo.strip()
        self.__telefono = telefono_limpio

    @property
    def nombre(self):
        """Devuelve el nombre encapsulado del cliente."""
        return self.__nombre

    @property
    def correo(self):
        """Devuelve el correo encapsulado del cliente."""
        return self.__correo

    @property
    def telefono(self):
        """Devuelve el teléfono encapsulado del cliente."""
        return self.__telefono

    def mostrar_informacion(self):
        """Retorna la información formateada del cliente."""
        return (
            f"Cliente [{self.identificador}]: {self.__nombre} | "
            f"Correo: {self.__correo} | "
            f"Teléfono: {self.__telefono}"
        )


# ==========================================================
# 5. CLASE ABSTRACTA SERVICIO
# ==========================================================
class Servicio(Entidad, ABC):
    """Clase abstracta base para los servicios que ofrece Software FJ."""

    def __init__(self, identificador, nombre, tarifa_base, disponible=True):
        super().__init__(identificador)  # Valida y guarda el identificador.

        # Valida el nombre del servicio.
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidosError("El nombre del servicio es obligatorio.")

        # Evita bool (en Python bool hereda de int) y exige número positivo.
        if isinstance(tarifa_base, bool) or not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise DatosInvalidosError("La tarifa base debe ser mayor a cero.")

        # Valida que la disponibilidad sea booleana.
        if not isinstance(disponible, bool):
            raise DatosInvalidosError("La disponibilidad debe ser True o False.")

        self._nombre = nombre.strip()  # Nombre del servicio.
        self._tarifa_base = float(tarifa_base)  # Tarifa base por unidad de duración.
        self._disponible = disponible  # Estado de disponibilidad del servicio.

    @property
    def nombre(self):
        """Retorna el nombre del servicio."""
        return self._nombre

    @property
    def disponible(self):
        """Indica si el servicio está disponible."""
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        """Cambia la disponibilidad del servicio y registra el evento en el log."""
        if not isinstance(estado, bool):
            raise DatosInvalidosError("El estado de disponibilidad debe ser booleano.")
        self._disponible = estado
        logging.info("Servicio %s cambio de disponibilidad a %s.", self.identificador, estado)

    @abstractmethod
    def validar_parametros(self, duracion):
        """Valida los parámetros propios del servicio."""
        pass

    @abstractmethod
    def calcular_costo(self, duracion, **kwargs):
        """Calcula el costo del servicio según duración y parámetros opcionales."""
        pass

    def mostrar_informacion(self):
        """Retorna el resumen del servicio."""
        estado_texto = "Disponible" if self._disponible else "No disponible"
        return (
            f"Servicio [{self.identificador}]: {self._nombre} | "
            f"Tarifa base: ${self._tarifa_base:,.0f} | "
            f"Estado: {estado_texto}"
        )


# ==========================================================
# 6. SERVICIO DE RESERVA DE SALAS
# ==========================================================
class ReservaSala(Servicio):
    """Servicio derivado para reservar salas de reuniones."""

    def validar_parametros(self, duracion):
        """Valida que la duración en horas sea positiva."""
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duración de la sala debe ser positiva.")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """Calcula el costo de la sala con impuesto y descuento opcionales."""
        self.validar_parametros(duracion)  # Valida duración.

        if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)) or impuesto < 0:
            raise DatosInvalidosError("El impuesto no puede ser negativo.")

        if isinstance(descuento, bool) or not isinstance(descuento, (int, float)) or not (0 <= descuento <= 100):
            raise DatosInvalidosError("El descuento debe estar entre 0 y 100.")

        subtotal = self._tarifa_base * duracion  # Costo base.
        con_descuento = subtotal * (1 - descuento / 100)  # Aplica descuento.
        return con_descuento * (1 + impuesto / 100)  # Aplica impuesto y retorna total.


# ==========================================================
# 7. SERVICIO DE ALQUILER DE EQUIPOS
# ==========================================================
class AlquilerEquipo(Servicio):
    """Servicio derivado para alquilar equipos tecnológicos."""

    def validar_parametros(self, duracion):
        """Valida que la duración del alquiler sea positiva."""
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duración del alquiler debe ser positiva.")

    def calcular_costo(self, duracion, descuento=0, impuesto=0):
        """Calcula el costo del alquiler con descuento e impuesto opcionales."""
        self.validar_parametros(duracion)  # Valida duración.

        if isinstance(descuento, bool) or not isinstance(descuento, (int, float)) or not (0 <= descuento <= 100):
            raise DatosInvalidosError("El descuento debe estar entre 0 y 100.")

        if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)) or impuesto < 0:
            raise DatosInvalidosError("El impuesto no puede ser negativo.")

        subtotal = self._tarifa_base * duracion  # Costo base.
        con_descuento = subtotal * (1 - descuento / 100)  # Aplica descuento.
        return con_descuento * (1 + impuesto / 100)  # Aplica impuesto y retorna total.


# ==========================================================
# 8. SERVICIO DE ASESORÍAS ESPECIALIZADAS
# ==========================================================
class Asesoria(Servicio):
    """Servicio derivado para asesorías especializadas."""

    def validar_parametros(self, duracion):
        """Valida que la duración de la asesoría sea positiva."""
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duración de la asesoría debe ser positiva.")

    def calcular_costo(self, duracion, impuesto=0):
        """Calcula el costo de la asesoría con impuesto opcional."""
        self.validar_parametros(duracion)  # Valida duración.

        if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)) or impuesto < 0:
            raise DatosInvalidosError("El impuesto no puede ser negativo.")

        subtotal = self._tarifa_base * duracion  # Costo base.
        return subtotal * (1 + impuesto / 100)  # Retorna total con impuesto si aplica.


# ==========================================================
# 9. CLASE RESERVA
# ==========================================================
class Reserva(Entidad):
    """Integra cliente, servicio, duración, costo y estado con control de excepciones."""

    def __init__(self, identificador, cliente, servicio, duracion, **opciones_costo):
        super().__init__(identificador)  # Valida y asigna ID de reserva.

        if not isinstance(cliente, Cliente):  # Verifica objeto Cliente válido.
            raise ReservaInvalidaError("Debe asociarse un cliente válido.")

        if not isinstance(servicio, Servicio):  # Verifica objeto Servicio válido.
            raise ReservaInvalidaError("Debe asociarse un servicio válido.")

        if not servicio.disponible:  # Impide reservar servicios no disponibles.
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no está disponible."
            )

        servicio.validar_parametros(duracion)  # Valida duración según el servicio.

        self._cliente = cliente  # Cliente que realiza la reserva.
        self._servicio = servicio  # Servicio reservado.
        self._duracion = duracion  # Duración solicitada.
        self._estado = "Pendiente"  # Estado inicial.
        self._costo = servicio.calcular_costo(duracion, **opciones_costo)  # Cálculo polimórfico.

    @property
    def estado(self):
        """Retorna el estado actual de la reserva."""
        return self._estado

    def confirmar(self):
        """Confirma la reserva si está pendiente."""
        if self._estado != "Pendiente":
            raise ReservaInvalidaError(
                f"No se puede confirmar una reserva en estado '{self._estado}'."
            )
        self._estado = "Confirmada"  # Actualiza estado.
        logging.info("Reserva %s confirmada.", self.identificador)

    def cancelar(self):
        """Cancela la reserva si aún no está cancelada."""
        if self._estado == "Cancelada":
            raise ReservaInvalidaError("La reserva ya se encuentra cancelada.")
        self._estado = "Cancelada"  # Actualiza estado.
        logging.info("Reserva %s cancelada.", self.identificador)

    def procesar(self):
        """Procesa la reserva empleando try/except/else/finally."""
        try:
            if self._estado == "Cancelada":
                raise ReservaInvalidaError("No se puede procesar una reserva cancelada.")
            self.confirmar()  # Confirma la reserva si aplica.
            print(f"Reserva {self.identificador} procesada correctamente.")
        except ReservaInvalidaError as error:
            logging.error("Error procesando reserva %s: %s", self.identificador, error)
            raise  # Relanza la excepción para manejarla arriba.
        else:
            logging.info("Reserva %s procesada sin errores.", self.identificador)
        finally:
            print(f"Finalizando intento de procesamiento de reserva {self.identificador}.")

    def mostrar_informacion(self):
        """Retorna el detalle de la reserva."""
        return (
            f"Reserva [{self.identificador}]: Cliente={self._cliente.nombre} | "
            f"Servicio={self._servicio.nombre} | Duración={self._duracion} | "
            f"Costo=${self._costo:,.0f} | Estado={self._estado}"
        )


# ==========================================================
# 10. SISTEMA INTEGRAL DE GESTIÓN (LISTAS EN MEMORIA)
# ==========================================================
class SistemaSoftwareFJ:
    """Administra clientes, servicios y reservas usando listas sin base de datos."""

    def __init__(self):
        self.clientes = []  # Lista de clientes registrados.
        self.servicios = []  # Lista de servicios registrados.
        self.reservas = []  # Lista de reservas creadas.

    def registrar_cliente(self, cliente):
        """Registra un cliente evitando duplicados."""
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El objeto no corresponde a un cliente.")
        if any(c.identificador == cliente.identificador for c in self.clientes):
            raise DatosInvalidosError("El cliente ya se encuentra registrado.")
        self.clientes.append(cliente)  # Añade a la lista interna.
        logging.info("Cliente registrado: %s", cliente.identificador)
        print("Cliente registrado correctamente.")

    def registrar_servicio(self, servicio):
        """Registra un servicio evitando duplicados."""
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El objeto no corresponde a un servicio.")
        if any(s.identificador == servicio.identificador for s in self.servicios):
            raise DatosInvalidosError("El servicio ya se encuentra registrado.")
        self.servicios.append(servicio)  # Añade a la lista interna.
        logging.info("Servicio registrado: %s", servicio.identificador)
        print("Servicio registrado correctamente.")

    def crear_reserva(self, reserva):
        """Registra una reserva evitando duplicados."""
        if not isinstance(reserva, Reserva):
            raise ReservaInvalidaError("El objeto no corresponde a una reserva.")
        if any(r.identificador == reserva.identificador for r in self.reservas):
            raise ReservaInvalidaError("El identificador de reserva ya existe.")
        self.reservas.append(reserva)  # Añade a la lista interna.
        logging.info("Reserva creada: %s", reserva.identificador)
        print("Reserva creada correctamente.")

    def mostrar_clientes(self):
        """Muestra todos los clientes registrados."""
        print("\n--- LISTADO DE CLIENTES ---")
        for cliente in self.clientes:
            print(cliente.mostrar_informacion())

    def mostrar_servicios(self):
        """Muestra todos los servicios registrados."""
        print("\n--- LISTADO DE SERVICIOS ---")
        for servicio in self.servicios:
            print(servicio.mostrar_informacion())

    def mostrar_reservas(self):
        """Muestra todas las reservas registradas."""
        print("\n--- LISTADO DE RESERVAS ---")
        for reserva in self.reservas:
            print(reserva.mostrar_informacion())


# ==========================================================
# 11. SIMULACIÓN DE OPERACIONES (15 OPERACIONES)
# ==========================================================
def ejecutar_simulacion():
    """Ejecuta operaciones válidas e inválidas verificando continuidad del sistema."""
    sistema = SistemaSoftwareFJ()  # Crea instancia del sistema.

    print("=" * 65)
    print(" SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ")
    print("=" * 65)

    # Operación 1: Registro de cliente válido.
    try:
        cliente1 = Cliente("C001", "Carlos Pérez", "carlos@email.com", "3001234567")
        sistema.registrar_cliente(cliente1)
    except ErrorSistema as error:
        logging.error("Operación 1: %s", error)
        print("Error:", error)

    # Operación 2: Registro de segundo cliente válido.
    try:
        cliente2 = Cliente("C002", "Laura Gómez", "laura@email.com", "3101234567")
        sistema.registrar_cliente(cliente2)
    except ErrorSistema as error:
        logging.error("Operación 2: %s", error)
        print("Error:", error)

    # Operación 3: Intento de registrar cliente con correo inválido.
    try:
        cliente_invalido = Cliente("C003", "Pedro Ruiz", "correo_invalido", "3201234567")
        sistema.registrar_cliente(cliente_invalido)
    except ErrorSistema as error:
        logging.error("Operación 3 controlada: %s", error)
        print("Operación 3 controlada:", error)

    # Operación 4: Creación de servicio de reserva de salas.
    try:
        sala = ReservaSala("S001", "Reserva de sala", 80000)
        sistema.registrar_servicio(sala)
    except ErrorSistema as error:
        logging.error("Operación 4: %s", error)
        print("Error:", error)

    # Operación 5: Creación de servicio de alquiler de equipos.
    try:
        equipo = AlquilerEquipo("S002", "Alquiler de equipos", 50000)
        sistema.registrar_servicio(equipo)
    except ErrorSistema as error:
        logging.error("Operación 5: %s", error)
        print("Error:", error)

    # Operación 6: Creación de servicio de asesoría especializada.
    try:
        asesoria = Asesoria("S003", "Asesoría especializada", 120000)
        sistema.registrar_servicio(asesoria)
    except ErrorSistema as error:
        logging.error("Operación 6: %s", error)
        print("Error:", error)

    # Operación 7: Intento de crear servicio con tarifa negativa.
    try:
        servicio_invalido = ReservaSala("S004", "Sala inválida", -1000)
        sistema.registrar_servicio(servicio_invalido)
    except ErrorSistema as error:
        logging.error("Operación 7 controlada: %s", error)
        print("Operación 7 controlada:", error)

    # Operación 8: Creación de reserva válida.
    try:
        reserva1 = Reserva("R001", cliente1, sala, 2)
        sistema.crear_reserva(reserva1)
    except ErrorSistema as error:
        logging.error("Operación 8: %s", error)
        print("Error:", error)

    # Operación 9: Confirmación de reserva válida.
    try:
        reserva1.confirmar()
        print("Operación 9: Reserva confirmada.")
    except ErrorSistema as error:
        logging.error("Operación 9: %s", error)
        print("Error:", error)

    # Operación 10: Intento de confirmar una reserva ya confirmada.
    try:
        reserva1.confirmar()
    except ErrorSistema as error:
        logging.error("Operación 10 controlada: %s", error)
        print("Operación 10 controlada:", error)

    # Operación 11: Intento de crear reserva con duración inválida.
    try:
        reserva_invalida = Reserva("R002", cliente2, equipo, 0)
        sistema.crear_reserva(reserva_invalida)
    except ErrorSistema as error:
        logging.error("Operación 11 controlada: %s", error)
        print("Operación 11 controlada:", error)

    # Operación 12: Intento de reservar un servicio marcado como no disponible.
    try:
        asesoria.cambiar_disponibilidad(False)  # Marca el servicio como no disponible.
        reserva_no_disp = Reserva("R003", cliente2, asesoria, 2)
        sistema.crear_reserva(reserva_no_disp)
    except ErrorSistema as error:
        logging.error("Operación 12 controlada: %s", error)
        print("Operación 12 controlada:", error)

    # Operación 13: Cancelación de reserva e intento posterior de procesarla.
    try:
        reserva1.cancelar()
        reserva1.procesar()
    except ErrorSistema as error:
        print("Operación 13 controlada:", error)

    # Operación 14: Cálculo de costos con impuesto y descuento opcionales.
    try:
        costo_sala = sala.calcular_costo(2, impuesto=19)
        costo_equipo = equipo.calcular_costo(3, descuento=10)
        print(f"Operación 14: Sala=${costo_sala:,.0f} | Equipo=${costo_equipo:,.0f}")
    except ErrorSistema as error:
        logging.error("Operación 14: %s", error)
        print("Error:", error)

    # Operación 15: Encadenamiento de excepciones (raise ... from ...).
    try:
        try:
            int("dato_no_numerico")  # Genera ValueError nativo.
        except ValueError as error_original:
            raise DatosInvalidosError(
                "No fue posible convertir el dato ingresado."
            ) from error_original  # Encadena la excepción original.
    except DatosInvalidosError as error:
        logging.exception("Operación 15: Excepción encadenada.")
        print("Operación 15 controlada:", error)

    # Muestra el estado final de las listas.
    sistema.mostrar_clientes()
    sistema.mostrar_servicios()
    sistema.mostrar_reservas()

    print("\nSimulación finalizada.")
    print("Los eventos y errores se registran en sistema.log.")


# ==========================================================
# 12. PUNTO DE ENTRADA DEL PROGRAMA
# ==========================================================
if __name__ == "__main__":
    try:
        ejecutar_simulacion()  # Ejecuta la simulación principal.
    except Exception as error:
        logging.exception("Error inesperado en la ejecución principal.")
        print("Se presentó un error inesperado:", error)
    finally:
        print("Aplicación Software FJ finalizada.")
