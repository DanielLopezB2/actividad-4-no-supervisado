# Instrucciones de ejecución

Agrupamiento de estaciones de TransMilenio (Bogotá) por perfil de demanda con KMeans y agrupamiento jerárquico (scikit-learn).

## 1. Requisitos

- Python 3.10 o superior (desarrollado con Python 3.14).
- Git.
- Dependencias: `pandas`, `scikit-learn`, `matplotlib`, `pytest` (en `requirements.txt`).

## 2. Instalación

```bash
git clone https://github.com/DanielLopezB2/actividad-4-no-supervisado.git
cd actividad-4-no-supervisado

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## 3. Ejecución

Todos los comandos se ejecutan desde la raíz del repositorio, con el entorno virtual activo.

| Paso | Comando | Qué hace |
|---|---|---|
| 1. Generar datos | `python -m src.dataset` | Escribe `data/station_profiles.csv` (1200 filas, semilla 42) y muestra un resumen |
| 2. Agrupar | `python -m src.cluster` | Elige k por silueta, ajusta KMeans y jerárquico, imprime métricas y composición de los grupos, y guarda dos gráficas en `docs/img/` |
| 3. Probar | `python -m pytest -v` | Ejecuta las 12 pruebas automatizadas |

Si falta `data/station_profiles.csv`, `src.cluster` lo genera automáticamente.

## 4. Cómo leer la salida de `src.cluster`

```text
Rows: 1200 | features: 19
Silhouette by k (KMeans):
  k=2: 0.496
  k=3: 0.608
  k=4: 0.618  <- chosen
  ...
ARI KMeans vs hierarchical:        1.000
ARI KMeans vs hidden archetype:    1.000  (validation only)

Cluster 0: 360 station-days | mean total 1679
  day types: {'weekday': 0.59, 'saturday': 0.21, 'sunday_holiday': 0.19}
  top stations: {'Portal Eldorado': 60, ...}
```

| Elemento | Significado |
|---|---|
| `features: 19` | 18 proporciones horarias del día más el logaritmo del volumen total |
| `Silhouette by k` | Calidad de la separación para cada k de 2 a 8; se elige el mayor (cerca de 1 es mejor) |
| `ARI KMeans vs hierarchical` | Concordancia entre ambos algoritmos (1.0 = particiones idénticas) |
| `ARI ... vs hidden archetype` | Validación contra el arquetipo oculto del generador; nunca se usa para ajustar |
| `Cluster N` | Tamaño, volumen diario medio, proporción por tipo de día y estaciones principales |

Las gráficas se guardan en `docs/img/clusters-pca.png` (plano PCA) y `docs/img/perfiles-cluster.png` (perfil horario medio por cluster).

## 5. Pruebas

```bash
python -m pytest -v
```

Resultado esperado: `12 passed`. El detalle está en `docs/informe-pruebas.md`.

## 6. Estructura del proyecto

```text
actividad-4/
├── README.md
├── requirements.txt
├── data/        # network.json (red) y station_profiles.csv (datos sintéticos)
├── docs/        # documentación e imágenes
├── src/         # dataset.py, cluster.py
└── tests/       # pruebas con pytest
```

## 7. Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'src'` | Se ejecutó fuera de la raíz o con `python src/cluster.py` | Ejecutar desde la raíz con `python -m src.cluster` |
| `ModuleNotFoundError: No module named 'pandas'` | Entorno virtual no activo o dependencias sin instalar | `source .venv/bin/activate` y `pip install -r requirements.txt` |
| Las tildes aparecen mal en la terminal | Codificación de la terminal distinta de UTF-8 | Configurar la terminal en UTF-8 |
