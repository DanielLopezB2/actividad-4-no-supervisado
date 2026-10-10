# Informe de pruebas

**Proyecto:** Agrupamiento de estaciones de TransMilenio (Bogotá) por perfil de demanda
**Curso:** Inteligencia Artificial, Corporación Universitaria Iberoamericana
**Actividad:** 4 - Métodos de aprendizaje no supervisado

## 1. Objetivo

Verificar que el generador de datos y el agrupamiento se comportan como se documenta, y reportar con evidencia real los resultados del modelo no supervisado. Todas las salidas de este informe se obtuvieron ejecutando el código del repositorio con semilla 42.

## 2. Entorno

| Elemento | Valor |
|---|---|
| Sistema operativo | macOS (Darwin) |
| Python | 3.14.7 |
| pytest | 9.1.1 |
| Bibliotecas | pandas, scikit-learn, matplotlib, pytest (`requirements.txt`) |

## 3. Resultados de `python -m pytest -v`

**Total: 12 pruebas, 12 aprobadas, 0 fallidas (2.29 s).**

```text
$ .venv/bin/python -m pytest -v
tests/test_cluster.py::test_features_have_no_nan_and_expected_width PASSED [  8%]
tests/test_cluster.py::test_hourly_shares_sum_to_one PASSED              [ 16%]
tests/test_cluster.py::test_choose_k_returns_k_in_range PASSED           [ 25%]
tests/test_cluster.py::test_choose_k_selects_four_archetypes PASSED      [ 33%]
tests/test_cluster.py::test_kmeans_beats_random_labels_on_silhouette PASSED [ 41%]
tests/test_cluster.py::test_kmeans_recovers_hidden_archetypes PASSED     [ 50%]
tests/test_cluster.py::test_hierarchical_agrees_with_kmeans PASSED       [ 58%]
tests/test_dataset.py::test_shape_and_columns PASSED                     [ 66%]
tests/test_dataset.py::test_no_nulls_and_valid_values PASSED             [ 75%]
tests/test_dataset.py::test_all_network_stations_have_an_archetype PASSED [ 83%]
tests/test_dataset.py::test_seed_reproducibility PASSED                  [ 91%]
tests/test_dataset.py::test_archetype_is_not_leaked_into_the_data PASSED [100%]

============================== 12 passed in 2.29s ==============================
```

### Qué verifica cada prueba

| Módulo | Prueba | Qué verifica |
|---|---|---|
| `test_dataset.py` | `test_shape_and_columns` | 1200 filas (20 estaciones × 60 días) y columnas exactas: `station`, `day_type`, `rain`, `h05`..`h22` |
| | `test_no_nulls_and_valid_values` | Sin nulos; `day_type` y `rain` con valores válidos; conteos no negativos y enteros |
| | `test_all_network_stations_have_an_archetype` | Cada estación de `network.json` tiene arquetipo asignado y viceversa |
| | `test_seed_reproducibility` | La misma semilla produce un DataFrame idéntico; una semilla distinta, datos distintos |
| | `test_archetype_is_not_leaked_into_the_data` | El arquetipo oculto no aparece como columna del CSV |
| `test_cluster.py` | `test_features_have_no_nan_and_expected_width` | La matriz de variables no tiene NaN y tiene 19 columnas (18 proporciones + volumen) |
| | `test_hourly_shares_sum_to_one` | Las proporciones horarias de cada fila suman 1 |
| | `test_choose_k_returns_k_in_range` | `choose_k` devuelve un k del rango 2..8 con la mayor silueta |
| | `test_choose_k_selects_four_archetypes` | Con el conjunto por defecto, la silueta elige k = 4, igual al número de arquetipos del generador |
| | `test_kmeans_beats_random_labels_on_silhouette` | La silueta de KMeans supera en más de 0.1 a la de etiquetas aleatorias |
| | `test_kmeans_recovers_hidden_archetypes` | El índice de Rand ajustado contra el arquetipo oculto es mayor que 0.6 |
| | `test_hierarchical_agrees_with_kmeans` | El agrupamiento jerárquico (Ward) coincide con KMeans (ARI mayor que 0.6) |

Las pruebas usan las funciones reales, sin simulaciones (mocks).

## 4. Resultados de `python -m src.dataset`

```text
$ .venv/bin/python -m src.dataset
Wrote 1200 rows x 21 columns to data/station_profiles.csv
day_type
weekday           0.614
saturday          0.194
sunday_holiday    0.192
rain share: 0.246
count    1200.0
mean     2037.0
std      1395.0
min       367.0
25%      1131.5
50%      1790.5
75%      2238.8
max      8038.0
```

## 5. Resultados de `python -m src.cluster`

Salida real:

```text
$ .venv/bin/python -m src.cluster
Rows: 1200 | features: 19
Silhouette by k (KMeans):
  k=2: 0.496
  k=3: 0.608
  k=4: 0.618  <- chosen
  k=5: 0.465
  k=6: 0.416
  k=7: 0.269
  k=8: 0.268

ARI KMeans vs hierarchical:        1.000
ARI KMeans vs hidden archetype:    1.000  (validation only)
ARI hierarchical vs archetype:     1.000  (validation only)

Cluster 0: 360 station-days | mean total 1679
  day types: {'weekday': 0.59, 'saturday': 0.21, 'sunday_holiday': 0.19}
  top stations: {'Portal Eldorado': 60, 'Modelia': 60, 'Normandía': 60, 'Portal Américas': 60, 'Banderas': 60}

Cluster 1: 240 station-days | mean total 963
  day types: {'weekday': 0.64, 'sunday_holiday': 0.18, 'saturday': 0.18}
  top stations: {'Av. Rojas': 60, 'Corferias': 60, 'Concejo de Bogotá': 60, 'Puente Aranda': 60}

Cluster 2: 420 station-days | mean total 1789
  day types: {'weekday': 0.64, 'saturday': 0.19, 'sunday_holiday': 0.17}
  top stations: {'Calle 100': 60, 'Héroes': 60, 'Calle 72': 60, 'Calle 63': 60, 'Calle 45': 60}

Cluster 3: 180 station-days | mean total 4763
  day types: {'weekday': 0.56, 'sunday_holiday': 0.26, 'saturday': 0.18}
  top stations: {'Calle 26': 60, 'Centro Memoria': 60, 'Ricaurte': 60}

Plots saved to docs/img
```

## 6. Interpretación de los resultados

### 6.1 Elección de k

| k | Silueta (KMeans) |
|---|---|
| 2 | 0.496 |
| 3 | 0.608 |
| **4** | **0.618** |
| 5 | 0.465 |
| 6 | 0.416 |
| 7 | 0.269 |
| 8 | 0.268 |

La silueta máxima está en k = 4 (0.618), igual al número de arquetipos del generador. Un valor cercano a 1 indica grupos compactos y bien separados; por encima de 0.6 se considera una estructura clara. La diferencia con k = 3 (0.608) es pequeña, de modo que k = 3 y k = 4 son casi equivalentes según el criterio; a partir de k = 5 la silueta cae con fuerza, señal de que se está partiendo grupos que ya eran compactos.

### 6.2 Grupos encontrados

| Cluster | Estación-días | Volumen diario medio | Perfil horario | Estaciones |
|---|---|---|---|---|
| 0 | 360 | 1679 | Pico marcado en la mañana (7 h, cerca del 20 % de los abordajes del día) | Portal Eldorado, Portal Américas, Banderas, Marsella, Modelia, Normandía |
| 1 | 240 | 963 | Un solo abultamiento amplio entre media mañana y la tarde (máximo a las 12 h, cerca del 11 %), sin picos de hora pico | Av. Rojas, Corferias, Concejo de Bogotá, Puente Aranda |
| 2 | 420 | 1789 | Pico marcado en la tarde (18 h, cerca del 16 % de los abordajes) y meseta al mediodía | Calle 100, Calle 72, Calle 63, Calle 45, Calle 34, Héroes, Calle 75 |
| 3 | 180 | 4763 | Tres picos: ambas horas pico (8 h y 18 h, cerca del 8 % cada una) y el mediodía (12-13 h, cerca del 9 %); el volumen es el más alto | Calle 26, Centro Memoria, Ricaurte |

Lectura: el cluster 0 corresponde a estaciones de origen residencial (los pasajeros salen en la mañana), el cluster 2 a estaciones de destino laboral (los pasajeros regresan en la tarde), el cluster 3 a nodos de transbordo (volumen alto y repartido en tres picos) y el cluster 1 a estaciones mixtas de volumen bajo. La proporción de tipos de día es parecida en los cuatro grupos (día hábil entre 0.56 y 0.64; con solo 3 a 7 estaciones por grupo, esas diferencias son variación de muestreo), lo que indica que el agrupamiento separa tipos de estación y no tipos de día.

![Perfil horario medio por cluster](img/perfiles-cluster.png)

![Estación-día en el plano PCA](img/clusters-pca.png)

El plano PCA explica 51 % y 31 % de la varianza (83 % en total). Los cuatro clusters forman nubes compactas y separadas.

### 6.3 Validación externa

| Comparación | ARI |
|---|---|
| KMeans frente a jerárquico (Ward) | 1.000 |
| KMeans frente a arquetipo oculto | 1.000 |
| Jerárquico frente a arquetipo oculto | 1.000 |

El arquetipo oculto **no se usa para ajustar** los modelos; solo se compara al final. Los dos algoritmos producen la misma partición (ARI 1.000) y esa partición coincide exactamente con los arquetipos del generador.

### 6.4 Separación de `hub` y `mixed`

En la primera versión del generador, `hub` y `mixed` tenían casi la misma forma horaria (plana, con picos suaves) y se distinguían solo por el volumen. La silueta elegía k = 3 (0.640) y los fusionaba, con un ARI de 0.859 frente al arquetipo. Para separarlos se ajustaron los supuestos del generador en `src/dataset.py` (no el algoritmo de agrupamiento ni los umbrales de las pruebas): `hub` pasó a tener tres picos (ambas horas pico y el mediodía), `mixed` pasó a un único abultamiento amplio sin picos de hora pico, y el volumen base de `mixed` subió de 60 a 70. La tabla cruzada entre el arquetipo oculto y el cluster asignado por KMeans es ahora:

| Arquetipo | Cluster 0 | Cluster 1 | Cluster 2 | Cluster 3 |
|---|---|---|---|---|
| `residential` | 360 | 0 | 0 | 0 |
| `business` | 0 | 0 | 420 | 0 |
| `hub` | 0 | 0 | 0 | 180 |
| `mixed` | 0 | 240 | 0 | 0 |

Esta separación se logró **ajustando nuestros propios supuestos sintéticos**. Por eso el resultado demuestra que el método recupera grupos bien diferenciados, no que las estaciones reales de TransMilenio se comporten así.

## 7. Limitaciones

- **Datos sintéticos.** Los grupos son los arquetipos escritos en `src/dataset.py` más ruido. El resultado ilustra el método, no es una afirmación sobre el comportamiento real de TransMilenio.
- **Separación a medida.** El ARI de 1.000 se obtuvo después de diseñar las formas horarias de `hub` y `mixed` para que fueran distinguibles (sección 6.4); con datos reales, grupos con perfiles parecidos podrían fusionarse.
- **Una sola configuración.** Los resultados corresponden a una semilla (42) y a 60 días por estación; con otra semilla se esperan diferencias pequeñas en las siluetas.
- **Validación externa disponible solo por ser sintéticos.** Con datos reales no existiría un arquetipo de referencia y solo se podría usar la silueta y la interpretación de los perfiles.

## 8. Reproducibilidad

Toda la aleatoriedad usa la semilla 42 (`SEED` en `src/dataset.py` y `src/cluster.py`). Ejecutar de nuevo `python -m src.dataset` y `python -m src.cluster` produce el mismo archivo y las mismas métricas. Las instrucciones están en `docs/INSTRUCCIONES.md`.
