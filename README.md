"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas.
Empresa: Software FJ
Curso: Programación (213023) - UNAD
Fase 4: Prácticas simuladas

Este módulo implementa una arquitectura orientada a objetos sin base de datos,
con manejo avanzado de excepciones, validaciones y registro en archivo de logs.
"""

from abc import ABC, abstractmethod  # Importa herramientas para definir clases y métodos abstractos.
import logging  # Importa el módulo estándar para registrar eventos y errores en archivos.


# ==========================================================
# 1. CONFIGURACIÓN DEL SISTEMA DE REGISTRO (LOGS)
# ==========================================================
logging.basicConfig(
    filename="sistema.log",  # Nombre del archivo donde se almacenarán los logs.
    level=logging.INFO,  # Nivel mínimo de registro (INFO, WARNING, ERROR, CRITICAL).
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato de fecha, severidad y mensaje.
    encoding="utf-8",  # Codificación UTF-8 para soportar tildes y caracteres especiales.
)


# ==========================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ==========================================================
class ErrorSistema(Exception):
    """Excepción base para todos los errores controlados del sistema Software FJ."""
    pass  # Hereda directamente de Exception sin añadir campos extra.


class DatosInvalidosError(ErrorSistema):
    """Se lanza cuando los datos ingresados no cumplen con las reglas o tipos esperados."""
    pass


class ServicioNoDisponibleError(ErrorSistema):
    """Se lanza cuando se intenta operar o reservar un servicio que no está disponible."""
    pass


class ReservaInvalidaError(ErrorSistema):
    """Se lanza cuando ocurre una operación inválida sobre una reserva o su estado."""
    pass


# ==========================================================
# 3. CLASE ABSTRACTA ENTIDAD
# ==========================================================
class Entidad(ABC):
    """Clase abstracta base que representa una entidad general del sistema."""

    def __init__(self, identificador):
        # Valida que el identificador exista y no sea una cadena vacía o solo espacios.
        if not identificador or not str(identificador).strip():
            raise DatosInvalidosError("El identificador es obligatorio.")  # Lanza excepción personalizada.
        self._identificador = str(identificador).strip()  # Atributo protegido con el ID limpio.

    @property
    def identificador(self):
        """Expone el identificador de forma controlada (solo lectura)."""
        return self._identificador  # Retorna el ID protegido.

    @abstractmethod
    def mostrar_informacion(self):
        """Método abstracto que obliga a las subclases a definir su representación textual."""
        pass


# ==========================================================
# 4. CLASE CLIENTE
# ==========================================================
class Cliente(Entidad):
    """Representa un cliente de Software FJ con encapsulación y validaciones estrictas."""

    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)  # Inicializa y valida el identificador en Entidad.

        # Valida que el nombre sea texto no vacío.
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidosError("El nombre del cliente es obligatorio.")

        # Valida que el correo contenga '@' y un dominio básico.
        if not isinstance(correo, str) or "@" not in correo or "." not in correo.split("@")[-1]:
            raise DatosInvalidosError("El correo electrónico no es válido.")

        telefono_str = str(telefono).strip()  # Convierte y limpia el teléfono a cadena.
        # Valida que el teléfono tenga solo dígitos y al menos 7 caracteres.
        if not telefono_str.isdigit() or len(telefono_str) < 7:
            raise DatosInvalidosError("El teléfono debe contener mínimo 7 dígitos numéricos.")

        # Encapsulación mediante atributos privados (__).
        self.__nombre = nombre.strip()  # Nombre encapsulado del cliente.
        self.__correo = correo.strip()  # Correo encapsulado del cliente.
        self.__telefono = telefono_str  # Teléfono encapsulado del cliente.

    @property
    def nombre(self):
        """Permite consultar el nombre del cliente de forma segura."""
        return self.__nombre

    @property
    def correo(self):
        """Permite consultar el correo del cliente de forma segura."""
        return self.__correo

    @property
    def telefono(self):
        """Permite consultar el teléfono del cliente de forma segura."""
        return self.__telefono

    def mostrar_informacion(self):
        """Retorna una cadena formateada con los datos del cliente."""
        return (
            f"Cliente [{self.identificador}]: {self.__nombre} | "
            f"Correo: {self.__correo} | "
            f"Teléfono: {self.__telefono}"
        )


# ==========================================================
# 5. CLASE ABSTRACTA SERVICIO
# ==========================================================
class Servicio(Entidad, ABC):
    """Clase abstracta para los servicios ofrecidos por Software FJ."""

    def __init__(self, identificador, nombre, tarifa_base, disponible=True):
        super().__init__(identificador)  # Valida y asigna el identificador.

        # Valida que el nombre del servicio sea válido.
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidosError("El nombre del servicio es obligatorio.")

        # Valida que la tarifa base sea numérica (evitando bool, ya que en Python bool es subclase de int).
        if isinstance(tarifa_base, bool) or not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise DatosInvalidosError("La tarifa base debe ser un número mayor a cero.")

        # Valida que la disponibilidad sea booleana.
        if not isinstance(disponible, bool):
            raise DatosInvalidosError("La disponibilidad debe ser un valor booleano (True/False).")

        self._nombre = nombre.strip()  # Nombre del servicio.
        self._tarifa_base = float(tarifa_base)  # Tarifa base convertida a flotante.
        self._disponible = disponible  # Indica si el servicio está disponible para reservar.

    @property
    def nombre(self):
        """Retorna el nombre del servicio."""
        return self._nombre

    @property
    def disponible(self):
        """Indica si el servicio se encuentra disponible."""
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        """Actualiza la disponibilidad del servicio."""
        if not isinstance(estado, bool):
            raise DatosInvalidosError("El estado de disponibilidad debe ser True o False.")
        self._disponible = estado  # Actualiza el estado interno.
        logging.info("Disponibilidad del servicio %s actualizada a %s.", self.identificador, estado)

    @abstractmethod
    def calcular_costo(self, duracion, **kwargs):
        """Calcula el costo del servicio según duración y parámetros opcionales."""
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        """Valida los parámetros específicos requeridos por el servicio."""
        pass

    def mostrar_informacion(self):
        """Muestra la información general del servicio."""
        estado_txt = "Disponible" if self._disponible else "No disponible"  # Texto legible de estado.
        return (
            f"Servicio [{self.identificador}]: {self._nombre} | "
            f"Tarifa base: ${self._tarifa_base:,.0f} | "
            f"Estado: {estado_txt}"
        )


# ==========================================================
# 6. SERVICIO DE RESERVA DE SALAS
# ==========================================================
class ReservaSala(Servicio):
    """Servicio especializado para la reserva de salas de reuniones."""

    def validar_parametros(self, duracion):
        """Valida que la duración en horas sea un número positivo."""
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duración de la reserva de sala debe ser positiva.")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """
        Calcula el costo de la sala soportando variantes mediante parámetros opcionales:
        - Solo duración: calcular_costo(2)
        - Duración e impuesto: calcular_costo(2, impuesto=19)
        - Duración, impuesto y descuento: calcular_costo(2, impuesto=19, descuento=10)
        """
        self.validar_parametros(duracion)  # Valida la duración antes de operar.

        if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)) or impuesto < 0:
            raise DatosInvalidosError("El porcentaje de impuesto no puede ser negativo.")

        if isinstance(descuento, bool) or not isinstance(descuento, (int, float)) or not (0 <= descuento <= 100):
            raise DatosInvalidosError("El porcentaje de descuento debe estar entre 0 y 100.")

        subtotal = self._tarifa_base * duracion  # Calcula el costo base por duración.
        con_descuento = subtotal * (1 - descuento / 100)  # Aplica porcentaje de descuento.
        total = con_descuento * (1 + impuesto / 100)  # Aplica porcentaje de impuesto sobre el subtotal ajustado.
        return total  # Retorna el costo final calculado.


# ==========================================================
# 7. SERVICIO DE ALQUILER DE EQUIPOS
# ==========================================================
class AlquilerEquipo(Servicio):
    """Servicio especializado para el alquiler de equipos tecnológicos."""

    def validar_parametros(self, duracion):
        """Valida que la duración del alquiler sea un número positivo."""
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duración del alquiler de equipos debe ser positiva.")

    def calcular_costo(self, duracion, descuento=0, impuesto=0):
        """
        Calcula el costo del alquiler con parámetros opcionales de descuento e impuesto.
        """
        self.validar_parametros(duracion)  # Valida la duración.

        if isinstance(descuento, bool) or not isinstance(descuento, (int, float)) or not (0 <= descuento <= 100):
            raise DatosInvalidosError("El descuento debe estar entre 0 y 100.")

        if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)) or impuesto < 0:
            raise DatosInvalidosError("El impuesto no puede ser negativo.")

        subtotal = self._tarifa_base * duracion  # Calcula subtotal inicial.
        con_descuento = subtotal * (1 - descuento / 100)  # Aplica descuento porcentual.
        total = con_descuento * (1 + impuesto / 100)  # Aplica impuesto porcentual.
        return total  # Retorna el total final.


# ==========================================================
# 8. SERVICIO DE ASESORÍAS ESPECIALIZADAS
# ==========================================================
class Asesoria(Servicio):
    """Servicio especializado para asesorías profesionales."""

    def validar_parametros(self, duracion):
        """Valida que la duración de la asesoría sea un número positivo."""
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duración de la asesoría debe ser positiva.")

    def calcular_costo(self, duracion, impuesto=0):
        """
        Calcula el costo de la asesoría según duración e impuesto opcional.
        """
        self.validar_parametros(duracion)  # Valida la duración.

        if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)) or impuesto < 0:
            raise DatosInvalidosError("El impuesto no puede ser negativo.")

        subtotal = self._tarifa_base * duracion  # Calcula costo base.
        return subtotal * (1 + impuesto / 100)  # Retorna total con impuesto si aplica.


# ==========================================================
# 9. CLASE RESERVA
# ==========================================================
class Reserva(Entidad):
    """Integra un cliente, un servicio, duración y estado con control de ciclo de vida."""

    def __init__(self, identificador, cliente, servicio, duracion, **parametros_costo):
        super().__init__(identificador)  # Valida y asigna el ID de la reserva.

        if not isinstance(cliente, Cliente):  # Verifica que el cliente sea instancia de Cliente.
            raise ReservaInvalidaError("Debe asociarse un cliente válido.")

        if not isinstance(servicio, Servicio):  # Verifica que el servicio sea instancia de Servicio.
            raise ReservaInvalidaError("Debe asociarse un servicio válido.")

        if not servicio.disponible:  # Verifica disponibilidad antes de crear la reserva.
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no se encuentra disponible actualmente."
            )

        servicio.validar_parametros(duracion)  # Valida la duración según las reglas del servicio.

        self._cliente = cliente  # Cliente asociado a la reserva.
        self._servicio = servicio  # Servicio reservado.
        self._duracion = duracion  # Duración solicitada.
        self._estado = "Pendiente"  # Estado inicial de toda nueva reserva.
        self._costo = servicio.calcular_costo(duracion, **parametros_costo)  # Calcula costo de forma polimórfica.

    @property
    def estado(self):
        """Retorna el estado actual de la reserva."""
        return self._estado

    @property
    def costo(self):
        """Retorna el costo calculado de la reserva."""
        return self._costo

    def confirmar(self):
        """Confirma una reserva únicamente si está en estado Pendiente."""
        if self._estado != "Pendiente":  # Evita confirmar reservas ya confirmadas o canceladas.
            raise ReservaInvalidaError(
                f"No se puede confirmar una reserva en estado '{self._estado}'."
            )

        self._estado = "Confirmada"  # Cambia el estado a Confirmada.
        logging.info("Reserva %s confirmada para el cliente %s.", self.identificador, self._cliente.nombre)

    def cancelar(self):
        """Cancela una reserva si no ha sido cancelada previamente."""
        if self._estado == "Cancelada":  # Evita doble cancelación.
            raise ReservaInvalidaError("La reserva ya se encuentra cancelada.")

        self._estado = "Cancelada"  # Cambia el estado a Cancelada.
        logging.info("Reserva %s cancelada.", self.identificador)

    def procesar(self):
        """Procesa la reserva usando try/except/else/finally y relanza errores controlados."""
        try:
            if self._estado == "Cancelada":  # Bloquea el procesamiento de reservas canceladas.
                raise ReservaInvalidaError("No se puede procesar una reserva cancelada.")

            self.confirmar()  # Intenta confirmar la reserva.
            print(f"Reserva {self.identificador} procesada y confirmada correctamente.")

        except ReservaInvalidaError as error:
            logging.error("Error al procesar la reserva %s: %s", self.identificador, error)  # Registra el error.
            raise  # Propaga la excepción para que la capa superior decida cómo manejarla.

        else:
            # Se ejecuta solo si el bloque try terminó sin lanzar excepciones.
            logging.info("Procesamiento exitoso completado para la reserva %s.", self.identificador)

        finally:
            # Se ejecuta siempre, haya ocurrido error o no.
            print(f"[FINALLY] Finalizando intento de procesamiento de la reserva {self.identificador}.")

    def mostrar_informacion(self):
        """Retorna el resumen completo de la reserva."""
        return (
            f"Reserva [{self.identificador}]: Cliente={self._cliente.nombre} | "
            f"Servicio={self._servicio.nombre} | Duración={self._duracion} | "
            f"Costo=${self._costo:,.0f} | Estado={self._estado}"
        )


# ==========================================================
# 10. SISTEMA INTEGRAL DE GESTIÓN (EN MEMORIA CON LISTAS)
# ==========================================================
class SistemaSoftwareFJ:
    """Gestiona clientes, servicios y reservas en memoria mediante listas."""

    def __init__(self):
        self.clientes = []  # Lista interna de objetos Cliente.
        self.servicios = []  # Lista interna de objetos Servicio.
        self.reservas = []  # Lista interna de objetos Reserva.

    def registrar_cliente(self, cliente):
        """Registra un cliente validando tipo y unicidad de identificador."""
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El objeto proporcionado no corresponde a un Cliente.")

        if any(c.identificador == cliente.identificador for c in self.clientes):
            raise DatosInvalidosError(f"Ya existe un cliente con el ID '{cliente.identificador}'.")

        self.clientes.append(cliente)  # Agrega el cliente a la lista.
        logging.info("Cliente registrado: %s - %s", cliente.identificador, cliente.nombre)
        print(f"Cliente '{cliente.nombre}' registrado correctamente.")

    def registrar_servicio(self, servicio):
        """Registra un servicio validando tipo y unicidad de identificador."""
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El objeto proporcionado no corresponde a un Servicio.")

        if any(s.identificador == servicio.identificador for s in self.servicios):
            raise DatosInvalidosError(f"Ya existe un servicio con el ID '{servicio.identificador}'.")

        self.servicios.append(servicio)  # Agrega el servicio a la lista.
        logging.info("Servicio registrado: %s - %s", servicio.identificador, servicio.nombre)
        print(f"Servicio '{servicio.nombre}' registrado correctamente.")

    def crear_reserva(self, reserva):
        """Registra una reserva en el sistema validando tipo y unicidad de ID."""
        if not isinstance(reserva, Reserva):
            raise ReservaInvalidaError("El objeto proporcionado no corresponde a una Reserva.")

        if any(r.identificador == reserva.identificador for r in self.reservas):
            raise ReservaInvalidaError(f"Ya existe una reserva con el ID '{reserva.identificador}'.")

        self.reservas.append(reserva)  # Agrega la reserva a la lista.
        logging.info("Reserva creada: %s", reserva.identificador)
        print(f"Reserva '{reserva.identificador}' creada correctamente.")

    def mostrar_clientes(self):
        """Imprime el listado de clientes registrados."""
        print("\n--- LISTADO DE CLIENTES ---")
        for cliente in self.clientes:
            print(cliente.mostrar_informacion())

    def mostrar_servicios(self):
        """Imprime el listado de servicios registrados."""
        print("\n--- LISTADO DE SERVICIOS ---")
        for servicio in self.servicios:
            print(servicio.mostrar_informacion())

    def mostrar_reservas(self):
        """Imprime el listado de reservas registradas."""
        print("\n--- LISTADO DE RESERVAS ---")
        for reserva in self.reservas:
            print(reserva.mostrar_informacion())


# ==========================================================
# 11. SIMULACIÓN DE OPERACIONES (MÍNIMO 10 OPERACIONES)
# ==========================================================
def ejecutar_simulacion():
    """Ejecuta operaciones válidas e inválidas para demostrar estabilidad y manejo de errores."""
    sistema = SistemaSoftwareFJ()  # Instancia el sistema de gestión.

    print("=" * 65)
    print(" SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ")
    print("=" * 65)

    # Operación 1: Registro de cliente válido.
    try:
        cliente1 = Cliente("C001", "Carlos Pérez", "carlos@email.com", "3001234567")
        sistema.registrar_cliente(cliente1)
    except ErrorSistema as error:
        logging.error("Operación 1 fallida: %s", error)
        print("Error en Operación 1:", error)

    # Operación 2: Registro de segundo cliente válido.
    try:
        cliente2 = Cliente("C002", "Laura Gómez", "laura@email.com", "3101234567")
        sistema.registrar_cliente(cliente2)
    except ErrorSistema as error:
        logging.error("Operación 2 fallida: %s", error)
        print("Error en Operación 2:", error)

    # Operación 3: Intento de registrar cliente con correo inválido.
    try:
        cliente_invalido = Cliente("C003", "Pedro Ruiz", "correo_sin_arroba", "3201234567")
        sistema.registrar_cliente(cliente_invalido)
    except ErrorSistema as error:
        logging.error("Operación 3 controlada: %s", error)
        print(f"Operación 3 controlada: {error}")

    # Operación 4: Creación de servicio de reserva de salas.
    try:
        sala = ReservaSala("S001", "Sala Ejecutiva A", 80000)
        sistema.registrar_servicio(sala)
    except ErrorSistema as error:
        logging.error("Operación 4 fallida: %s", error)
        print("Error en Operación 4:", error)

    # Operación 5: Creación de servicio de alquiler de equipos.
    try:
        equipo = AlquilerEquipo("S002", "Portátil Empresarial i7", 50000)
        sistema.registrar_servicio(equipo)
    except ErrorSistema as error:
        logging.error("Operación 5 fallida: %s", error)
        print("Error en Operación 5:", error)

    # Operación 6: Creación de servicio de asesoría especializada.
    try:
        asesoria = Asesoria("S003", "Consultoría en Arquitectura de Software", 120000)
        sistema.registrar_servicio(asesoria)
    except ErrorSistema as error:
        logging.error("Operación 6 fallida: %s", error)
        print("Error en Operación 6:", error)

    # Operación 7: Intento de crear servicio con tarifa negativa.
    try:
        servicio_invalido = ReservaSala("S004", "Sala Inválida", -15000)
        sistema.registrar_servicio(servicio_invalido)
    except ErrorSistema as error:
        logging.error("Operación 7 controlada: %s", error)
        print(f"Operación 7 controlada: {error}")

    # Operación 8: Creación de reserva válida.
    try:
        reserva1 = Reserva("R001", cliente1, sala, 2)
        sistema.crear_reserva(reserva1)
    except ErrorSistema as error:
        logging.error("Operación 8 fallida: %s", error)
        print("Error en Operación 8:", error)

    # Operación 9: Procesamiento (confirmación) de reserva válida usando try/except/else/finally.
    try:
        reserva1.procesar()
    except ErrorSistema as error:
        print(f"Operación 9 controlada: {error}")

    # Operación 10: Intento de confirmar nuevamente una reserva ya confirmada.
    try:
        reserva1.confirmar()
    except ErrorSistema as error:
        logging.error("Operación 10 controlada: %s", error)
        print(f"Operación 10 controlada: {error}")

    # Operación 11: Intento de crear reserva con duración inválida.
    try:
        reserva_duracion_invalida = Reserva("R002", cliente2, equipo, 0)
        sistema.crear_reserva(reserva_duracion_invalida)
    except ErrorSistema as error:
        logging.error("Operación 11 controlada: %s", error)
        print(f"Operación 11 controlada: {error}")

    # Operación 12: Intento de reservar un servicio marcado como no disponible.
    try:
        asesoria.cambiar_disponibilidad(False)  # Marca la asesoría como no disponible.
        reserva_no_disp = Reserva("R003", cliente2, asesoria, 3)
        sistema.crear_reserva(reserva_no_disp)
    except ErrorSistema as error:
        logging.error("Operación 12 controlada: %s", error)
        print(f"Operación 12 controlada: {error}")

    # Operación 13: Cancelación de reserva válida e intento posterior de procesarla.
    try:
        reserva1.cancelar()
        reserva1.procesar()
    except ErrorSistema as error:
        print(f"Operación 13 controlada: {error}")

    # Operación 14: Cálculo de costo con impuesto y descuento opcionales.
    try:
        costo_sala_imp = sala.calcular_costo(2, impuesto=19)
        costo_equipo_desc = equipo.calcular_costo(3, descuento=15)
        print(f"Operación 14: Costo sala (2h + 19% IVA): ${costo_sala_imp:,.0f} | Costo equipo (3h - 15% desc): ${costo_equipo_desc:,.0f}")
    except ErrorSistema as error:
        logging.error("Operación 14 fallida: %s", error)
        print("Error en Operación 14:", error)

    # Operación 15: Encadenamiento de excepciones (raise ... from ...).
    try:
        try:
            horas_ingresadas = int("dos_horas")  # Provoca ValueError nativo de Python.
        except ValueError as error_original:
            raise DatosInvalidosError(
                "La duración ingresada no es un número entero válido."
            ) from error_original  # Encadena la excepción original.
    except DatosInvalidosError as error:
        logging.exception("Operación 15 controlada mediante encadenamiento de excepciones.")
        print(f"Operación 15 controlada: {error} (Causa original: {error.__cause__})")

    # Muestra el estado final de todas las listas en memoria.
    sistema.mostrar_clientes()
    sistema.mostrar_servicios()
    sistema.mostrar_reservas()

    print("\nSimulación finalizada con éxito. Revisa 'sistema.log' para el historial completo.")


# ==========================================================
# 12. PUNTO DE ENTRADA DEL PROGRAMA
# ==========================================================
if __name__ == "__main__":
    try:
        ejecutar_simulacion()  # Ejecuta la simulación principal.
    except Exception as error:
        # Captura cualquier error inesperado no contemplado anteriormente.
        logging.exception("Error crítico inesperado en la ejecución principal.")
        print("Se presentó un error inesperado:", error)
    finally:
        print("Aplicación Software FJ finalizada.")




        
