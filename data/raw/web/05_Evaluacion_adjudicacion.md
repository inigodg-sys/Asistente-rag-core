# 5. Evaluación y adjudicación

El proceso de evaluación consiste en cinco (5) etapas consecutivas que son revisadas por la Comisión.  
- La primera etapa corresponde a la **apertura de las ofertas técnicas**, en la que se revisa que se encuentren todos los documentos requeridos y se cumpla con los plazos y exigencias de las bases.  
- La segunda etapa es la de **evaluación de admisibilidad**, en la cual la Comisión revisa y analiza los antecedentes generales y técnicos de los oferentes.  
- En la tercera etapa se realiza la **evaluación de la oferta técnica**.  
- La cuarta etapa es la **apertura de la oferta económica**, en la cual se revisa que la oferta cumpla con los criterios exigidos.  
- En la quinta etapa se realizan de manera simultánea la **evaluación de la oferta económica** y la **evaluación final**, en la que se ponderan los puntajes obtenidos en la evaluación técnica y económica.

El cronograma detallado de estas etapas se establece en el Artículo 3.4.1 de las bases (Tabla de etapas y plazos), cuyo contenido se ha estructurado en el CSV:

**CSV asociado (cronograma):** `data/raw/csv/cronograma_licitacion.csv`

---

## 5.1 Apertura de las ofertas técnicas

La apertura de las ofertas técnicas será realizada por la Comisión, en un acto público, en la oportunidad señalada en el cronograma del Artículo 3.4.1 de las bases. El Ministerio podrá determinar que el acto de apertura admita la asistencia de los oferentes de manera presencial o que se transmita vía streaming u otra modalidad que permita la participación a distancia. Lo anterior se informará debidamente con al menos diez (10) días hábiles de anticipación a través del sitio web.

En este acto se abrirán solo los sobres o paquetes N° 1 y N° 2 (antecedentes y oferta técnica), con el objeto de verificar que se han incluido los Documentos 1 al 13 señalados en los Artículos 4.1 y 4.2 de las bases. El contenido se evaluará en las etapas posteriores. Los sobres o paquetes de las ofertas económicas se mantendrán sellados y en custodia del Ministerio, sin abrir, hasta la apertura de las ofertas económicas (Artículo 5.4).

La Comisión levantará un acta de apertura que contendrá:
- la individualización de los integrantes de la Comisión presentes;
- las ofertas técnicas abiertas;
- la constatación de si cada oferta contiene los Documentos 1 al 13 requeridos por los Artículos 4.1 y 4.2.

Además, la Comisión dejará constancia en el acta de aquellas ofertas que se proponga declarar inadmisibles por:

- haberse presentado fuera del plazo establecido en las bases;  
- no haber presentado alguno de los Documentos 1 al 13 señalados en los Artículos 4.1 y 4.2;  
- incumplimiento de cualquier otra exigencia sustancial o requisito esencial establecido en las bases.

El acta de apertura se publicará en el sitio web, sin perjuicio de que el Ministerio pueda comunicarla también por correo electrónico a los oferentes. Las ofertas inadmisibles no pasan a la etapa de evaluación descrita en el Artículo 5.3.

En el acto de apertura no se admitirán recursos administrativos ni solicitudes de explicaciones o aclaraciones de ningún tipo.

---

## 5.2 Evaluación de admisibilidad

En esta etapa, la Comisión analiza el contenido de los documentos relativos a los **antecedentes generales** (Artículo 4.1) y determina:

- si el oferente cumple con los requisitos generales establecidos en el Artículo 3.3.1;  
- si se encuentra inhabilitado según las causales del Artículo 3.3.2.

Además, se verifica el cumplimiento de todos los elementos solicitados como antecedentes técnicos requeridos en el Artículo 4.2, que no están sujetos a asignación de puntaje pero deben cumplir un estándar de completitud y exactitud conforme a los Anexos.

De esta etapa se levanta un acta.  
Las ofertas que cumplan con las exigencias pasan a la etapa de evaluación técnica.  
Las que no cumplan la totalidad de las exigencias se declaran inadmisibles.

---

## 5.3 Evaluación técnica

En esta etapa, la Comisión evalúa las propuestas técnicas de los oferentes y asigna un puntaje a cada oferta de acuerdo con los siguientes criterios:

- **Experiencia en Gestión de Flota (EGF)** (GF1, GF2, GF3)  
- **Experiencia en Información a Personas Usuarias (EIPU)**  
- **Experiencia en Contadores de Personas Usuarias (ECPU)**  
- **Funcionalidades (F)**  
- **Plan de Capacitación (PC)**  

El puntaje técnico (PT) se calcula mediante:

> **PT = 0,35·EGF + 0,15·EIPU + 0,10·ECPU + 0,35·F + 0,05·PC**

Las ofertas con **PT ≥ 70** avanzan a la apertura económica.

---

### 5.3.1 Experiencia en Gestión de Flota (EGF)

> **EGF = 0,35·GF1 + 0,50·GF2 + 0,15·GF3**

Reglas:
- Si el puntaje ponderado final de EGF es < 50 → EGF = 0.  
- Si GF1 = 0 o GF2 = 0 o GF3 = 0 → EGF = 0.

---

#### 5.3.1.1 GF1 — Cantidad de buses con software SGF

Se otorga puntaje según la cantidad de buses monitoreados con el software de Gestión de Flota ofertado en el Anexo A06 (o alguna de sus versiones anteriores), en proyectos correspondientes a servicios de transporte público urbano.

**CSV asociado (rangos GF1):** `data/raw/csv/experiencia_gf1.csv`

---

#### 5.3.1.2 GF2 — Cantidad de computadores embarcados

Se otorga puntaje según la cantidad de computadores provistos y embarcados en buses, correspondientes al computador ofertado en el Anexo A06 (o alguna de sus versiones anteriores), en proyectos correspondientes a servicios de transporte público urbano.

**CSV asociado (rangos GF2):** `data/raw/csv/experiencia_gf2.csv`

El puntaje GF2 se calcula como:

> **GF2 = min( Σ Puntajes_CE , 100 )**

donde Σ Puntajes_CE es la suma de los puntajes asignados a los proyectos acreditados.

---

#### 5.3.1.3 GF3 — Soporte y mantenimiento

Se otorga puntaje según la cantidad de proyectos en que se presta o ha prestado servicio de soporte y mantenimiento a flotas de transporte.

El cálculo es:

> **GF3 = min(100 · (QFlotas_SM / 8), 100)**

donde QFlotas_SM es el número de proyectos con soporte/mantenimiento (umbral = 8).

---

### 5.3.2 Experiencia en información a personas usuarias (EIPU)

Se otorga puntaje según la cantidad de buses en los que se ha implementado una solución de información a personas usuarias, en proyectos de transporte público urbano.

**CSV asociado (rangos EIPU):** `data/raw/csv/experiencia_eipu.csv`

El puntaje se calcula como:

> **EIPU = min( Σ Puntajes_EIPU , 100 )**

---

### 5.3.3 Experiencia en contadores de personas usuarias (ECPU)

Se otorga puntaje según la cantidad de proyectos que cuentan con una solución de contadores de personas usuarias instalada en al menos un 10% de la flota, con precisión ≥ 95%.

El puntaje se calcula como:

> **ECPU = min(100 · (QFlotas_CP / 5), 100)**

donde QFlotas_CP es el número de proyectos acreditados (umbral = 5).

---

### 5.3.4 Funcionalidades (F)

Se otorga puntaje por la cantidad de funcionalidades adicionales implementadas, según el Anexo A10.

> **F = Σ_i ( S_i · W_i )**

donde S_i es 1 si se cumple la funcionalidad i y W_i es el peso asignado en A10.

La demostración funcional se detalla en el apartado 5.3.4.1 de las bases.

---

### 5.3.5 Plan de capacitación (PC)

El puntaje por Plan de Capacitación se asigna en función de las horas de capacitador ofertadas, según lo dispuesto en el Anexo A11 y la Tabla N° 5 del Artículo 5.3.5.

**CSV asociado (tramos de horas PC):** `data/raw/csv/plan_capacitacion_pc.csv`

En el evento de que el oferente que resulte adjudicado haya ofertado menos de mil (1.000) horas de capacitador, deberá en cualquier caso prestar como mínimo mil (1.000) horas de capacitador.

---

## 5.4 Apertura de ofertas económicas

La apertura de las ofertas económicas se realiza por la Comisión en un acto público, en el plazo señalado en el cronograma del Artículo 3.4.1. El Ministerio puede determinar si el acto es presencial o vía streaming u otro medio a distancia, informándolo con al menos diez (10) días hábiles de anticipación a través del sitio web.

En este acto se abren las ofertas económicas asociadas a las ofertas técnicamente aceptables (Artículo 5.3).

La Comisión levanta un acta de apertura que consigna:
- la individualización de los integrantes presentes;
- las ofertas económicas abiertas;
- la constatación de si cada oferta contiene toda la información requerida por el Artículo 4.3.

Las ofertas económicas que no cumplan las exigencias de las bases se proponen como inadmisibles, quedando constancia en el acta. Las restantes pasan a la evaluación económica.

El acta se publica en el sitio web y puede también remitirse por correo electrónico a los oferentes. No se admiten recursos ni aclaraciones en este acto.

---

## 5.5 Evaluación económica

Para el cálculo del puntaje económico de cada oferta se utilizan valores truncados a dos decimales. La evaluación económica se divide en dos etapas.

### 5.5.1 Etapa 1 — Costo mensual

Primero, se determina un valor económico para cada oferta, asociado al **costo mensual en pesos chilenos** que representa la oferta para el Sistema, en base a los valores del Anexo A12 (oferta económica) y el Artículo 4.3.

La fórmula general es:

> **CM_y = (PO_y + PI_y / 144) · UF**

donde:
- **CM_y**: costo mensual de la oferta y, en pesos chilenos, sin decimales, sin aproximación;  
- **PO_y**: pago de operación mensual ofertado para los servicios del contrato;  
- **PI_y**: pago de inversión ofertado, prorrateado en 144 cuotas mensuales;  
- **UF**: valor de la Unidad de Fomento del último día hábil del mes anterior al término del plazo de presentación de ofertas.

---

### 5.5.2 Etapa 2 — Puntaje económico

Luego, se calcula un puntaje económico para cada oferta según una escala relativa basada en todas las ofertas técnicamente aceptables:

> **PE_y = 100 · ( 1 - (CM_y - min(CM)) / (max(CM) - min(CM)) )**

donde:
- **PE_y**: puntaje económico de la oferta y;  
- **CM_y**: costo mensual de la oferta y;  
- **min(CM)**: mínimo valor de CM entre las ofertas técnicamente aceptables;  
- **max(CM)**: máximo valor de CM entre las ofertas técnicamente aceptables.

De este modo se asigna un puntaje económico (PE_y) entre 0 y 100.

---

## 5.6 Evaluación final

Tras la evaluación económica, la Comisión calcula el **puntaje final (PF_y)** de cada oferta, ponderando los puntajes técnico y económico:

> **PF_y = 0,5 · PT_y + 0,5 · PE_y**

donde:
- **PF_y**: puntaje final de la oferta y;  
- **PT_y**: puntaje técnico obtenido en la evaluación técnica;  
- **PE_y**: puntaje económico obtenido en la evaluación económica.

La oferta que obtenga el mayor puntaje final será la oferta a adjudicar.

La Comisión dejará constancia de los resultados de la evaluación económica y final en un acta única.

---

## 5.7 Adjudicación

De acuerdo con lo señalado, la licitación se adjudica al oferente cuya oferta obtenga el mayor puntaje final (PF_y).

Si el costo mensual de la oferta económica de un oferente es inferior al **promedio de los costos mensuales** de las demás ofertas, en un porcentaje igual o superior al **10%** (oferta temeraria), el Ministerio podrá, mediante resolución fundada, adjudicarla solicitando un **aumento en el monto de la garantía de fiel cumplimiento del contrato**, conforme a la cláusula 11.1 del Contrato.

Si solo hay dos oferentes, el porcentaje indicado se calculará respecto de la oferta superior. Si el adjudicatario no acepta aumentar la garantía, su oferta se considera desistida y se adjudica al siguiente oferente con mejor puntaje final.

En caso de empate entre dos o más ofertas, se aplican, en este orden, los criterios de desempate:

1. Mayor puntaje en la Evaluación Económica (PE_y).  
2. Mayor puntaje en la Evaluación Técnica (PT_y).  

Si el empate persiste, la adjudicación se resuelve mediante sorteo: se asigna un boleto a cada oferta empatada, se depositan en una urna y un miembro de la Comisión extrae uno. El boleto extraído corresponde al adjudicatario. El sorteo se realiza ante notario público.

El resultado del proceso de adjudicación se formaliza mediante la resolución de adjudicación, que, una vez totalmente tramitada, se publica en el sitio web y puede comunicarse por correo electrónico a los oferentes.
