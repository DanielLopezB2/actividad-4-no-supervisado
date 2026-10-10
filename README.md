# Agrupamiento de estaciones de transporte masivo por perfil de demanda

## Descripción general

Este proyecto aplica aprendizaje no supervisado a la red de TransMilenio (Bogotá) usada en las actividades anteriores (4 líneas, 20 estaciones). Agrupa **estación-días** (los abordajes por hora de una estación durante un día) en arquetipos de demanda, sin usar etiquetas: estaciones de origen residencial, de destino laboral, nodos de transbordo y estaciones mixtas de volumen bajo.

El sistema combina:

- Un conjunto de datos sintético reproducible.
- KMeans con selección de k por coeficiente de silueta.
- Agrupamiento jerárquico (Ward) como segundo método de comparación.
- Visualización con PCA y perfiles horarios medios por grupo.
- Validación externa contra un arquetipo oculto del generador.
- Pruebas automatizadas.

## Propósito académico

El proyecto demuestra la aplicación de conceptos de inteligencia artificial relacionados con:

1. Aprendizaje no supervisado (agrupamiento).
2. Técnicas de agrupamiento particional y jerárquico.
3. Evaluación sin etiquetas (silueta) y con referencia externa (índice de Rand ajustado).
4. Reducción de dimensionalidad para visualizar los grupos.

## Inicio rápido

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m src.dataset   # escribe data/station_profiles.csv
python -m src.cluster   # agrupa, imprime métricas y guarda las gráficas
python -m pytest
```

## Fuente de datos

No existe un conjunto de datos público de abordajes por estación y hora para esta red, por lo que los datos son **sintéticos**: `src/dataset.py` los genera a partir de supuestos explícitos, no de mediciones reales de TransMilenio. Las estaciones provienen de `data/network.json` (la misma red aproximada de las actividades anteriores).

Cada fila es una estación-día con `station`, `day_type`, `rain` y 18 conteos horarios `h05`..`h22` (20 estaciones × 60 días = 1200 filas, semilla 42). Cada estación pertenece a un arquetipo oculto (`residential`, `business`, `hub`, `mixed`) que fija la forma de su perfil horario; ese arquetipo no se guarda en el CSV ni se usa para ajustar los modelos.

La consecuencia es importante: el agrupamiento solo puede redescubrir los arquetipos escritos en el generador (más ruido). Los resultados ilustran el método y no dicen nada sobre el comportamiento real de los pasajeros.

Detalle completo en [`docs/descripcion-datos.md`](docs/descripcion-datos.md).

## Modelo y evaluación

Las variables son las 18 proporciones horarias del total del día (la forma del perfil) más el logaritmo del volumen diario, estandarizadas. Resultados de `python -m src.cluster` con semilla 42:

| Métrica | Valor |
| --- | --- |
| k elegido por silueta (rango 2 a 8) | 4 |
| Silueta con k = 4 (k = 3) | 0.618 (0.608) |
| ARI KMeans frente a jerárquico | 1.000 |
| ARI KMeans frente al arquetipo oculto | 1.000 |

| Cluster | Estación-días | Perfil | Estaciones |
| --- | --- | --- | --- |
| 0 | 360 | Pico de mañana (7 h) | Portal Eldorado, Portal Américas, Banderas, Marsella, Modelia, Normandía |
| 1 | 240 | Abultamiento amplio al mediodía, volumen bajo | Av. Rojas, Corferias, Concejo de Bogotá, Puente Aranda |
| 2 | 420 | Pico de tarde (18 h) | Calle 100, Calle 72, Calle 63, Calle 45, Calle 34, Héroes, Calle 75 |
| 3 | 180 | Tres picos (8, 12-13 y 18 h), volumen alto | Calle 26, Centro Memoria, Ricaurte |

**Nota:** en una primera versión `hub` y `mixed` tenían una forma horaria casi igual y la silueta los fusionaba (k = 3, ARI 0.859). Se separaron ajustando nuestros propios supuestos sintéticos; el ARI de 1.000 demuestra el método, no estructura real. Se documenta en el informe de pruebas (sección 6.4).

![Perfil horario medio por cluster](docs/img/perfiles-cluster.png)

Informe completo con salidas reales: [`docs/informe-pruebas.md`](docs/informe-pruebas.md) (también en [PDF](docs/informe-pruebas.pdf)).

## Documentación

| Documento | Contenido |
| --- | --- |
| [`docs/descripcion-datos.md`](docs/descripcion-datos.md) | Origen, diccionario de datos, arquetipos, supuestos y limitaciones |
| [`docs/informe-pruebas.md`](docs/informe-pruebas.md) | Pruebas automatizadas, ejecución real y análisis de métricas |
| [`docs/INSTRUCCIONES.md`](docs/INSTRUCCIONES.md) | Instalación y ejecución paso a paso |

## Estructura del proyecto

```text
actividad-4/
├── README.md
├── requirements.txt
├── data/
│   ├── network.json            # estaciones y líneas (estimaciones aproximadas)
│   └── station_profiles.csv    # conjunto de datos sintético (generado)
├── docs/
│   ├── descripcion-datos.md
│   ├── informe-pruebas.md
│   ├── informe-pruebas.pdf
│   ├── INSTRUCCIONES.md
│   └── img/                    # clusters-pca.png, perfiles-cluster.png (generadas)
├── src/
│   ├── dataset.py              # generador de datos sintéticos
│   └── cluster.py              # variables, KMeans, jerárquico, métricas y gráficas
└── tests/
```

## Entregables de la actividad

| # | Entregable | Ubicación |
|---|---|---|
| 1 | Archivos de fuentes de datos | `data/station_profiles.csv`, `data/network.json` |
| 2 | Código fuente en Python | `src/dataset.py`, `src/cluster.py` |
| 3 | Documento con la descripción de los datos | `docs/descripcion-datos.md` |
| 4 | Documento con las pruebas realizadas | `docs/informe-pruebas.md` y `docs/informe-pruebas.pdf` |
| 5 | Video (máximo 10 minutos) | Enlace indicado en la entrega de la tarea |

## Limitaciones

- El conjunto de datos es sintético; la demanda real depende de factores no modelados (incidentes, calendarios escolares, oferta de buses).
- Los arquetipos se eligen a mano, de modo que la recuperación casi perfecta de los grupos ilustra el método y no es una afirmación de desempeño real.
- La separación de `hub` y `mixed` se logró diseñando sus formas horarias; con k = 3 la silueta es casi igual (0.608 frente a 0.618), de modo que la elección de k = 4 es válida pero no abismalmente mejor.
- Los resultados corresponden a una sola semilla (42); con otras se esperan diferencias pequeñas.
