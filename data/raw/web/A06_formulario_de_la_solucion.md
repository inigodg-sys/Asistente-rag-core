# Anexo A06 – Formulario de la Solución  
*(Basado en el contenido oficial del Anexo A06 – Res 14-2023 Subsecretaría de Transportes)*

El Oferente debe proporcionar la información correspondiente a la solución SGF (Sistema de Gestión de Flota) y SIPU (Sistema de Información a Personas Usuarias) que propone para el Sistema de Transporte Público Metropolitano. Toda la información declarada es vinculante durante la vigencia del contrato y pasa a formar parte del Apéndice N°11 del Contrato en caso de adjudicación.

---

# A. Instrucciones para completar el Formulario A06

1. La solución ofertada debe ser consistente con la experiencia acreditada en los anexos A07, A08 y A09.  
2. Si la solución no incluye todos los campos obligatorios o no cumple los mínimos técnicos, la oferta será declarada inadmisible.  
3. El contexto operativo actual del Sistema considera aproximadamente **7.000 buses** distribuidos en clases A, B, C y D.  
4. Todas las características, certificaciones y capacidades mínimas declaradas deben ajustarse a lo indicado en el Contrato y en los Apéndices correspondientes.

---

# 1. Diagrama esquemático de la arquitectura

El Oferente debe incluir un **diagrama esquemático completo** que represente:

- Equipos embarcados (computador, consola, contador, modem).  
- Componentes del Sistema Central.  
- Interacción con COF (Centro de Operación de Flota).  
- Interacción con CMB (Centro de Monitoreo de Buses).  
- Integración SGF ↔ SIPU ↔ Comunicaciones.  
- Flujo de información entre bus ↔ servicios ↔ backend.  

El diagrama debe ser acompañado por una **descripción detallada**.

*(Este campo se completa por el oferente, no requiere CSV.)*

---

# 2. Arquitectura mínima de la solución

El Oferente debe completar las Tablas N°2, N°3, N°4 y N°5 del Formulario A06 según los estándares indicados en las Bases.  
La falta de completitud o especificaciones por debajo del mínimo implica inadmisibilidad.

### Tabla N° 1 – Componentes mínimos requeridos


| Nº | Arquitectura mínima solicitada |
|----|--------------------------------|
| 1  | Computador embarcado           |
| 2  | Consola del personal de conducción |
| 3  | Sistema de contador de personas usuarias |
| 4  | Dispositivo de comunicación del bus |

---

# 2.1 Computador embarcado en el bus

El computador embarcado debe ser el **centro de procesamiento**, capaz de:

- ejecutar funcionalidades SGF y SIPU;  
- orquestar los equipos a bordo;  
- gestionar comunicaciones;  
- registrar datos;  
- cumplir con 4.15, 4.16 y 4.17 del Contrato;  
- cumplir Apartado 5.4 del Apéndice N°1.

Debe instalarse en un gabinete o rack no accesible para el conductor (se prohíben tablets).

## Especificaciones mínimas
### Tabla N° 2 – Especificaciones mínimas del computador embarcado


| Categoría | Requisito |
|-----------|-----------|
| Procesador | ≥ 2 núcleos, 1.3 GHz |
| RAM | ≥ 4 GB |
| SSD | ≥ 60 GB |
| RS232/RS485 | ≥ 1 |
| Ethernet | ≥ 4 |
| USB | ≥ 2 |
| Entradas digitales/analógicas | ≥ 5 |
| Salidas digitales/analógicas | ≥ 5 |
| Puerto J1939 | Requerido |
| WiFi | IEEE 802.11 b/g/n |
| Módem | 2 slots SIM |
| Sensores | Acelerómetro y giroscopio |

**CSV asociado:** `data/raw/csv/a06_computador_embarcado.csv`

---

# 2.2 Consola táctil del personal de conducción

La consola debe:

- ser táctil;  
- tener pantalla a color;  
- mostrar información gráfica y textual;  
- ser capaz de reproducir audio;  
- permitir interacción con COF;  
- incluir micrófono cuello de ganso (no integrado).

## Especificaciones mínimas
### Tabla N° 3 – Especificaciones mínimas de la consola del personal de conducción


| Categoría | Requisito |
|-----------|-----------|
| Pantalla | PCAP retroiluminada |
| Dimensión | ≥ 7 pulgadas |
| Brillo/contraste | Ajustables |
| Alarma audible | Ajustable |
| Micrófono | Cuello de ganso, no desmontable |

**CSV asociado:** `data/raw/csv/a06_consola_conductor.csv`

---

# 2.3 Sistema de contador de personas usuarias

Debe cumplir:

- Registrar subidas y bajadas por puerta.  
- Diferenciar eventos simultáneos.  
- No debe verse afectado por clima o luminosidad.  
- Registrar todos los pasajeros sin excepción (<90 cm no requerido).  
- Identificar bicicletas y sillas de ruedas.  
- Resistencia al vandalismo.  
- Precisión mínima: **98%** (según Apéndice N°1, 3.1.6.1.1).

## Especificaciones mínimas
### Tabla N° 4 – Especificaciones mínimas del sistema de contador de personas usuarias


| Categoría | Requisito |
|-----------|-----------|
| Precisión | ≥ 98% |
| Identificación universal | Requerido |
| Detección de bicicletas | Requerido |
| Detección de sillas de ruedas | Requerido |
| Instalación resistente | Requerido |

**CSV asociado:** `data/raw/csv/a06_contador_personas.csv`

---

# 2.4 Dispositivo de comunicación del bus

Debe disponer de:

- Módem 4G o superior  
- 2 slots SIM  
- Certificación industrial  
- Diagrama de interconexión  
- Ancho de banda suficiente  
- Tecnologías inalámbricas declaradas  
- Sistema de respaldo  
- Protocolo de pruebas

## Especificaciones mínimas
### Tabla N° 5 – Especificaciones mínimas del dispositivo de comunicación del bus


| Categoría | Requisito |
|-----------|-----------|
| Tecnología | 4G o superior |
| SIM | 2 slots |
| Certificación | Industrial |
| Diagrama | Requerido |
| Respaldo comunicaciones | Requerido |

**CSV asociado:** `data/raw/csv/a06_modem_bus.csv`

---

# 3. Otros componentes de la solución

## Componentes obligatorios
### Tabla N° 6 – Componentes de hardware de la solución

| Componente | Descripción |
|------------|-------------|
| AVL | Sistema de localización automática |
| Megafonía (usuarios) | Audio e información embarcada |
| Megafonía (conductor) | Comunicación operativa |
| Pedal/botón de pánico | Activación de alertas |
| Estación COF | Puestos para operadores |
| Equipamiento CMB | Soporte a monitoreo |
| Equipamiento en terminales | Infraestructura local |
| Servicio de comunicaciones | SGF ↔ COF ↔ CMB |

**CSV asociado:** `data/raw/csv/a06_componentes_hardware.csv`

---

# B. Formulario A06 (campos a completar por el oferente)

El formulario original solicita:

- Nombre del oferente  
- Identificación de la solución  
- Arquitectura propuesta  
- Tablas 1 al 6 completas  
- Firmas del oferente/mandatario  

*(Estos campos no requieren CSV y permanecen como texto libre.)*

---

# FIN DEL ANEXO A06
