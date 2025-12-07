# Modelo de Documento y Estrategia de Chunking  
## Diseño Conceptual del Asistente RAG para la Licitación GF 001/2023  
### TFM – Big School (Iñaki Diez · 2025)

---

## 1. Introducción

El objetivo de este proyecto es desarrollar un asistente RAG (Retrieval-Augmented Generation) capaz de leer, interpretar y recuperar información desde el corpus completo de la licitación pública GF 001/2023. El sistema debe responder exclusivamente basándose en dicho corpus, garantizando trazabilidad normativa, precisión técnica y ausencia de alucinaciones.

Para alcanzar estos objetivos, el primer paso crítico es definir un modelo unificado de representación del conocimiento, denominado *modelo de documento*, junto con una estrategia de chunking coherente con la estructura del pliego y sus anexos.

Este documento describe el diseño conceptual adoptado, justificando cada decisión desde una perspectiva técnica y académica.

---

## 2. Naturaleza del Corpus

La licitación GF 001/2023 es un corpus heterogéneo compuesto por:

- Capítulos normativos (Cap. 1–6) en formato Markdown.
- Anexos A02–A13, incluyendo requerimientos técnicos, formularios y criterios evaluativos.
- Tablas normalizadas en CSV (GF1, GF2, GF3, EIPU, ECPU, funcionalidades, plan de capacitación).
- Definiciones estructuradas del pliego en formato JSON.
- El documento técnico “Rag (2)” como guía de buenas prácticas RAG.

Dada esta diversidad, es necesario establecer un modelo semántico uniforme que permita a los embeddings y al índice vectorial trabajar de manera consistente.

---

## 3. Necesidad de un Modelo de Documento Unificado

Un sistema RAG profesional no puede operar simplemente concatenando texto. Cada documento posee estructura, contexto y relaciones jerárquicas, especialmente en un ámbito regulado como una licitación pública.

Ejemplos:

- Los apartados del Capítulo 5 definen criterios de evaluación estrictamente numerados.
- El Anexo A10 contiene un conjunto de funcionalidades obligatorias y adicionales con pesos específicos.
- Las tablas CSV asignan rangos y puntajes que deben recuperarse correctamente.
- Las definiciones del Capítulo 2 poseen valor normativo y deben preservarse con exactitud.

Un modelo de documento permite:

1. Homogeneizar formatos dispares (MD, CSV, JSON).
2. Mantener trazabilidad absoluta.
3. Facilitar el filtrado y la recuperación semántica.
4. Asegurar el alineamiento técnico con un caso real de licitación pública.

---

## 4. El Modelo de Chunk

Cada fragmento de información extraído del corpus se representa mediante un objeto estructurado con la siguiente forma lógica:

- text  
- source  
- doc_type  
- section  
- id  
- tags  
- metadatos

Un ejemplo conceptual de chunk sería:

- text: “En GF1, un proyecto con 2000–3999 buses recibe 15 puntos según Art. 5.3.1.1.”  
- source: “data/raw/csv/experiencia_gf1.csv”  
- doc_type: “tabla”  
- section: “5.3.1.1.GF1”  
- id: “GF1-rango-2000-3999”  
- tags: [“GF1”, “evaluacion”, “rangos_buses”]  
- metadatos: { fila: 3, columna: “puntos”, valor: 15 }

### Justificación de los campos

- text:  
  Es el contenido limpio y normalizado que se utilizará para generar embeddings. Debe ser semánticamente claro y autosuficiente.

- source:  
  Indica el archivo de origen (“Capítulo 5”, “A06”, CSV concreto, etc.). Es esencial para la trazabilidad y para poder reconstruir la evidencia en el documento original.

- doc_type:  
  Permite distinguir entre normativa, formularios, tablas, definiciones o documentos tutoriales. Esta distinción facilita aplicar filtros y estrategias de recuperación más precisas.

- section:  
  Representa la ubicación jerárquica real dentro del pliego o del anexo (por ejemplo, 5.3.1.1, A06.2.1, A10.3.2.14). Este campo es clave para citas normativas exactas.

- id:  
  Es un identificador interno para auditoría, debugging y evaluación. Permite referirse a un chunk concreto sin depender únicamente del texto.

- tags:  
  Etiquetas temáticas (por ejemplo: “GF1”, “hardware”, “SIPU”, “funcionalidades”) que permiten agrupar y filtrar chunks por temas o dimensiones relevantes de la licitación.

- metadatos:  
  Campo flexible para almacenar información adicional dependiente del tipo de documento (número de fila en un CSV, nombre de columna, término definido en un JSON, número de página, etc.).

---

## 5. Estrategia de Chunking por Tipo de Documento

La estrategia de chunking se adapta al tipo de documento y a su función dentro del corpus. No se trocea de la misma forma un artículo normativo, una tabla de rangos o una definición.

### 5.1 Normativa (Capítulos 1–6 y Anexos A02–A13)

Para la normativa, se aplican las siguientes reglas:

- Segmentación por secciones y subsecciones (basadas en títulos, numeraciones y estructura jerárquica).
- Tamaño objetivo aproximado de 600–900 caracteres por chunk.
- Overlap de unos 120 caracteres entre chunks para preservar el contexto continuo.
- Conservación estricta de la numeración original (por ejemplo, 5.3.1.1, 5.3.2, A06.2.1).

Esta estrategia garantiza que cada chunk:

- Contenga suficiente contexto para ser interpretable.  
- Se pueda citar de forma normativamente correcta.  
- Mantenga las referencias internas del pliego.

### 5.2 Tablas CSV (GF1, GF2, GF3, EIPU, ECPU, funcionalidades, plan de capacitación)

Las tablas CSV no se indexan directamente como celdas sueltas, sino como frases semánticas:

- Cada fila de una tabla se convierte en un texto legible en lenguaje natural.
- Se incluye referencia al artículo o sección relevante del pliego.

Ejemplo de conversión:

- Fila CSV: rango 2000–3999, puntos 15.  
- Frase correspondiente: “En GF1, un proyecto con 2000–3999 buses recibe 15 puntos según Art. 5.3.1.1.”

Ventajas:

- Los modelos de lenguaje entienden la información de forma directa.  
- Se mantiene la trazabilidad a la tabla original a través de source, section y metadatos.  
- Se pueden responder preguntas cuantitativas (puntos, rangos, pesos) con precisión.

### 5.3 Definiciones (JSON)

Las definiciones del capítulo 2 se representan con chunks de la forma:

- text: “COF: Unidad del OST encargada de supervisar el desempeño de la prestación de servicios.”  
- source: “data/raw/json/definiciones.json”  
- doc_type: “definicion”  
- section: “2.8”  
- tags: [“definicion”, “COF”]

La exactitud de estas definiciones es crucial, ya que constituyen el vocabulario controlado de la licitación. Esta estrategia:

- Minimiza alucinaciones en términos clave.  
- Obliga al asistente a usar la terminología oficial del pliego.

### 5.4 Documento técnico “Rag (2)”

El documento “Rag (2)” se usa como guía interna de buenas prácticas RAG. Se chunkifica únicamente para:

- documentar el razonamiento técnico y pedagógico del proyecto,  
- apoyar la redacción del TFM.

No se emplea como fuente para responder preguntas del usuario sobre la licitación, por lo que se marca con doc_type “tutorial” y se excluye del contexto normativo.

---

## 6. Metadatos y Trazabilidad Normativa

La trazabilidad es un requisito esencial en este proyecto:

- Cada respuesta debe estar respaldada por uno o varios chunks concretos.  
- Cada chunk debe poder ubicarse de nuevo en el documento original.  
- Debe ser posible citar la sección o tabla exacta de la que procede la información.

El uso de los campos section, source, doc_type y metadatos permite:

- Reconstruir la evidencia normativa (artículos, anexos, tablas).  
- Explicar al usuario de dónde proviene cada afirmación.  
- Evaluar la fidelidad (faithfulness) de las respuestas generadas.

Ejemplos de respuestas trazables:

- “Según el Anexo A06, sección 2.1, el computador embarcado debe disponer de al menos 4 GB de RAM y 60 GB de almacenamiento SSD.”  
- “De acuerdo con la Tabla GF1, Art. 5.3.1.1, un rango de 2000–3999 buses obtiene 15 puntos.”

---

## 7. Alineación con los Objetivos del TFM

El diseño del modelo de documento y de la estrategia de chunking está alineado con los objetivos generales del TFM:

- Permite una evaluación rigurosa de la calidad del RAG (Recall@k, MRR, Faithfulness).  
- Asegura que el sistema se comporta de forma responsable frente a un corpus normativo real.  
- Favorece una narrativa arquitectónica clara, adecuada al nivel de un Trabajo Fin de Máster.  
- Facilita tu aprendizaje profundo del ciclo completo de un sistema RAG profesional.

---

## 8. Conclusión

El modelo de documento y la estrategia de chunking constituyen la base conceptual del asistente RAG desarrollado para la licitación GF 001/2023. Gracias a este diseño, el sistema puede operar de forma precisa sobre un corpus heterogéneo, manteniendo en todo momento la coherencia, la trazabilidad y el rigor normativo.

Este enfoque sienta las bases para la siguiente fase del proyecto: la implementación de la ingesta, indexación, recuperación y evaluación del sistema RAG, manteniendo la alineación entre los requisitos del pliego, las buenas prácticas técnicas y los objetivos académicos del TFM.

---
