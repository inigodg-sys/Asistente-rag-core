# A10 Apartado 3: Descripciones Técnicas de las Funcionalidades

## 3.1 Funcionalidades Mandatorias

### 3.1.1 Esquemas lineales tipo sinóptico
Representa el recorrido en forma lineal.
Incluye paradas, hitos y estructura general del servicio.

### 3.1.2 Datos operacionales
Muestra información operacional en tiempo real.
Incluye horarios, distancias, e indicadores clave.

### 3.1.3 Localización y visualización de buses
Muestra la posición del bus en tiempo real.
Indica dirección, movimiento y estado.

### 3.1.4 Velocidades
Registra y muestra la velocidad instantánea del bus.
Permite detectar excesos y anomalías.

### 3.1.5 Cálculos asociados a la operación
Calcula intervalos, headway, retrasos y distancias.
Provee métricas operacionales relevantes.

### 3.1.6 Regularidad
Evalúa la regularidad del servicio.
Identifica pérdida de frecuencia y desfases.

### 3.1.7 Expediciones
Monitorea el cumplimiento de las expediciones asignadas.

### 3.1.8 Inyecciones (bucle)
Detecta buses que ingresan o salen del circuito operacional.
Controla inyecciones y retiros.

### 3.1.9 Servicios con desvío en ruta
Detecta servicios que operan fuera de la ruta comercial definida.

### 3.1.10 Inicio de servicio
Registra el inicio formal del servicio del conductor.

### 3.1.11 Fin de servicio
Registra el término formal del servicio.

### 3.1.12 Seguimiento de inicio y fin de servicio
Monitorea en tiempo real qué buses iniciaron y terminaron.

### 3.1.13 Herramientas de apoyo a la conducción
Ofrece indicaciones al conductor sobre retraso/adelanto.
Incluye alertas visuales o auditivas.

### 3.1.14 Desvíos de ruta
Permite gestionar desvíos planificados o no planificados.

### 3.1.15 Playback histórico
Reproduce el movimiento histórico de los buses.

### 3.1.16 Sistema AVL
Localización automática del vehículo (GPS).
Reporte frecuente de posición y velocidad.

### 3.1.17 Programación de la operación
Gestión de servicios, horarios y tablas de viaje.

### 3.1.18 Sistema de puertas, timbre y rampa
Registro del estado de puertas, timbre y rampa accesible.

### 3.1.19 Letreros exteriores de información variable
Controla mensajes del letrero exterior del bus.

### 3.1.20 Incidencias: desvíos
Registro y monitoreo de incidencias vinculadas a desvíos.

### 3.1.21 Incidencias: regulación
Registro de acciones de regulación operacional.

### 3.1.22 Incidencias: inyecciones
Registro de incidencias relacionadas a incorporación/retiro de buses.

### 3.1.23 Reporte de configuración
Genera reportes sobre configuraciones del sistema y dispositivos.

### 3.1.24 Reporte de operación del día
Reporte consolidado del desempeño del servicio.

### 3.1.25 Herramientas de despacho
Emisión y control de órdenes de despacho.

### 3.1.26 Comunicaciones: anuncios grupales
Envío simultáneo de avisos a grupos de buses.

### 3.1.27 Comunicaciones: voz centro → buses
Canal de voz desde centro a conductores.

### 3.1.28 Comunicaciones: voz bus → centro
Canal de voz desde conductor al centro.

### 3.1.29 Mensajería centro → conductor
Envío de mensajes operativos al bus.

### 3.1.30 Mensajería conductor → centro
Envío de mensajes desde conductor hacia centro.

### 3.1.31 Servicio de generación de predicciones
Genera predicciones de arribo o avance en tiempo real.

### 3.1.32 Servicio de posicionamiento en línea
Servicio continuo de datos operativos en tiempo real.

### 3.1.33 Información de servicios, rutas y horarios
Administración de rutas, servicios y horarios.

### 3.1.34 GTFS-S (Schedule)
Soporte para publicación de datos estáticos GTFS-S.

### 3.1.35 GTFS-RT (Realtime)
Soporte para publicación de datos dinámicos GTFS-RT.

### 3.1.36 Gestión de mensajes
Gestión de plantillas y contenido operativo.

### 3.1.37 Gestor de contenidos
Gestión de textos, imágenes y contenido mostrado a usuarios.

### 3.1.38 Información a bordo
Mensajes de audio/visual dentro del bus: paradas, avisos, etc.

### 3.1.39 Megafonía a usuarios
Reproducción de avisos de audio para pasajeros.

## 3.2 Funcionalidades Adicionales

### 3.2.1 Aglomeraciones
Detección de zonas con alta concentración de usuarios.

### 3.2.2 Servicios no comerciales
Identifica buses operando en movimientos internos (pruebas, traslado).

### 3.2.3 Vistas portátiles
Interfaces para tablets o dispositivos móviles.

### 3.2.4 Transbordos e intermodalidad
Identificación de conexiones con otros sistemas de transporte.

### 3.2.5 Simulación de servicio
Simula operación para análisis y entrenamiento.

### 3.2.6 Retención y órdenes de salida
Permite emitir instrucciones de retención/salida desde terminal.

### 3.2.7 Retorno a terminal
Detección y gestión de retornos a terminal por contingencias.

### 3.2.8 Suspensión de puntos de parada
Deshabilita temporalmente puntos de parada afectados.

### 3.2.9 Reemplazo de punto de parada
Define paradas alternativas ante contingencias.

### 3.2.10 Modificación horaria
Modifica tablas horarias para contingencias operativas.

### 3.2.11 Gestión por tramos
Gestiona segmentos específicos del recorrido.

### 3.2.12 Extensión de servicio
Amplía el recorrido en zonas puntuales.

### 3.2.13 Registro de actividades
Registro de las acciones ejecutadas por el centro.

### 3.2.14 Contador avanzado
Analítica de conteo con capacidades extendidas.

### 3.2.15 Panel de control
Dashboard avanzado de operación y alertas.

### 3.2.16 Videovigilancia en tiempo real
Visualización en vivo de cámaras embarcadas.

### 3.2.17 ADAS – asistencia al conductor
Alertas de proximidad, obstáculos y riesgos.

### 3.2.18 Recursos Humanos (RRHH)
Integración con sistemas de turnos/asistencia del conductor.

### 3.2.19 API para terceros
Publicación de datos operativos vía API.

### 3.2.20 Integración con mantenimiento
Intercambio de fallas y eventos con sistemas de mantenimiento.

### 3.2.21 Identificación de servicios alterados
Detecta operaciones con comportamiento anómalo.

### 3.2.22 Identificación de paradas alteradas
Detecta paradas con funcionamiento anómalo o fuera de servicio.

### 3.2.23 Aglomeraciones de usuarios
Detección avanzada de acumulaciones de personas.

### 3.2.24 Mantenimiento avanzado
Predicción y gestión avanzada de mantenimiento.

### 3.2.25 Botón de pánico
Activación de alerta prioritaria.

### 3.2.26 Velocidades avanzadas
Alertas avanzadas por velocidad irregular.

### 3.2.27 Reporte de maniobras
Registro detallado de maniobras ejecutadas.

### 3.2.28 Eco-conducción
Evaluación del comportamiento de conducción.

### 3.2.29 Estadísticas de llamadas bus–centro
Registro de llamadas críticas y operativas.

### 3.2.30 Telemetría avanzada
Panel con alertas, sensores y parámetros mecánicos.

### 3.2.31 Gestión de despachos
Creación/modificación de despachos según operación.

### 3.2.32 Llamada urgente
Canal priorizado de comunicación con el centro.

### 3.2.33 Predictor vía API
Servicio predictor disponible vía API.

### 3.2.34 Predictor vía web
Servicio predictor accesible desde navegador.

### 3.2.35 Información mediante apps externas
Entrega data operacional a aplicaciones externas.

### 3.2.36 Desvíos/disrupciones
Comunicación de contingencias a las personas usuarias.

### 3.2.37 Ocupación en tiempo real
Muestra ocupación de pasajeros en vivo.

### 3.2.38 Estándar SIRI
Interfaz para intercambio de datos en tiempo real bajo estándar SIRI.

### 3.2.39 Información por zonas geográficas
Información contextual basada en zonas o áreas del sistema.

FIN DEL ANEXO A10 – Apartado 3