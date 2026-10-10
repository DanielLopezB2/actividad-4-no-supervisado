# Descripción de los datos

**Proyecto:** Agrupamiento de estaciones de TransMilenio (Bogotá) por perfil de demanda
**Archivo de datos:** `data/station_profiles.csv` (1200 filas, 21 columnas)
**Generador:** `src/dataset.py`

## 1. Origen de los datos

Los datos son **sintéticos**. No provienen de mediciones reales de TransMilenio: no existe un conjunto público de abordajes por estación y hora para esta red que se haya podido usar en la actividad. Se generan con `src/dataset.py` a partir de:

| Insumo | Fuente | Naturaleza |
|---|---|---|
| Estaciones | `data/network.json` (misma red de las actividades 2 y 3) | Red reducida de 4 líneas y 20 estaciones; tiempos y coordenadas aproximados |
| Forma del perfil horario de cada tipo de estación | Funciones gaussianas elegidas por el autor | Supuesto |
| Volumen base, factor por tipo de día y por lluvia | Constantes elegidas por el autor | Supuesto |
| Ruido de cada día | Poisson por hora y multiplicador lognormal por día | Supuesto |

Los valores son estimaciones plausibles para uso académico, no calibradas con datos reales.

## 2. Unidad de observación

Cada fila es una **estación-día**: los abordajes por hora de una estación durante un día. Hay 20 estaciones y 60 días observados por estación (`N_DAYS = 60`), es decir, 20 × 60 = 1200 filas. La semilla es 42 (`SEED`), por lo que el archivo es reproducible.

## 3. Diccionario de datos

| Columna | Tipo | Valores permitidos | Significado |
|---|---|---|---|
| `station` | texto (categórica) | 20 nombres de estación de `network.json` (por ejemplo `Calle 100`, `Ricaurte`, `Héroes`) | Estación observada |
| `day_type` | texto (categórica) | `weekday`, `saturday`, `sunday_holiday` | Tipo de día |
| `rain` | entero (0/1) | 0, 1 | 1 si llovió ese día |
| `h05` ... `h22` | entero (>= 0) | 18 columnas, una por hora de 5 a 22 (`h05`, `h06`, ..., `h22`) | Abordajes en esa hora (formato 24 h) |

No hay valores nulos ni conteos negativos (verificado por `tests/test_dataset.py`).

## 4. Arquetipo oculto (verdad de referencia)

Cada estación se asigna a un arquetipo de demanda al generar los datos. El arquetipo **no se guarda en el CSV** y **no se usa para ajustar** ningún modelo; solo sirve para validar los grupos encontrados (índice de Rand ajustado) y en las pruebas automatizadas. Una prueba verifica que la columna no se filtre al archivo.

| Arquetipo | Forma del perfil | Estaciones (`ARCHETYPES`) |
|---|---|---|
| `residential` | Pico fuerte de salida en la mañana (hacia las 7 h) | Portal Eldorado, Portal Américas, Banderas, Marsella, Modelia, Normandía |
| `business` | Pico fuerte en la tarde (hacia las 18 h) y meseta al mediodía | Calle 100, Calle 72, Calle 63, Calle 45, Calle 34, Héroes, Calle 75 |
| `hub` | Volumen alto y plano durante el día, con ambos picos | Calle 26, Centro Memoria, Ricaurte |
| `mixed` | Volumen bajo a moderado y plano, picos suaves | Av. Rojas, Corferias, Concejo de Bogotá, Puente Aranda |

Conteo de estaciones: 6 + 7 + 3 + 4 = 20.

## 5. Supuestos de generación

Para cada estación-día:

```text
nivel = VOLUMEN_BASE[arquetipo] · FACTOR_DIA[day_type] · FACTOR_LLUVIA · LogNormal(0, 0.12)
h_hh  ~ Poisson(nivel · FORMA[arquetipo][hora])
```

Constantes tomadas de `src/dataset.py`:

| Constante | Valor | Significado |
|---|---|---|
| `DAY_TYPE_PROBS` | `weekday` 0.6, `saturday` 0.2, `sunday_holiday` 0.2 | Probabilidad de cada tipo de día |
| `DAY_FACTOR` | `weekday` 1.0, `saturday` 0.7, `sunday_holiday` 0.45 | Escala el volumen según el tipo de día |
| `RAIN_PROB` | 0.25 | Probabilidad de lluvia en un día |
| `RAIN_FACTOR` | 1.1 | Aumento de volumen los días de lluvia |
| `NOISE_SIGMA` | 0.12 | Sigma del multiplicador lognormal de cada día |
| `BASE_VOLUME` | `residential` 140, `business` 120, `hub` 260, `mixed` 60 | Abordajes por hora de referencia |

Forma horaria relativa por arquetipo (`SHAPES`, unidades arbitrarias; `bump(c, a, h)` es una gaussiana de centro `c`, ancho `a` y altura `h`):

| Arquetipo | Forma |
|---|---|
| `residential` | 0.25 + bump(7, 1.2, 2.6) + bump(18, 1.5, 0.5) |
| `business` | 0.30 + bump(18, 1.2, 2.4) + bump(13, 2.5, 0.7) |
| `hub` | 0.90 + bump(7.5, 1.3, 0.8) + bump(17.5, 1.3, 0.8) |
| `mixed` | 0.80 + bump(8, 1.5, 0.3) + bump(17, 1.5, 0.3) |

## 6. Distribución del conjunto generado

Valores reales de `python -m src.dataset`:

| Variable | Resultado |
|---|---|
| `day_type` | `weekday` 0.601, `saturday` 0.208, `sunday_holiday` 0.191 |
| `rain` (proporción de días con lluvia) | 0.243 |
| Total diario de abordajes | media 2010.8, desviación 1403.4, mínimo 342, mediana 1777.5, máximo 7874 |

Cada estación aporta exactamente 60 filas.

## 7. Variables para el agrupamiento

`src/cluster.py` construye 19 variables por fila (18 + 1) y no usa `station`, `day_type`, `rain` ni el arquetipo:

1. **Forma del perfil:** los 18 conteos horarios divididos por el total del día (proporciones que suman 1). Así se compara el patrón de uso y no el tamaño de la estación.
2. **Volumen:** logaritmo natural del total diario de abordajes.

Todas las variables se estandarizan con `StandardScaler` (media 0, desviación 1) antes de agrupar.

## 8. Limitaciones

- Los datos son sintéticos: los grupos que se encuentren son los arquetipos escritos en el generador más ruido, no comportamiento real de pasajeros.
- Los arquetipos `hub` y `mixed` tienen una forma plana parecida; la diferencia principal entre ambos es el volumen, y el algoritmo puede fusionarlos (ver `docs/informe-pruebas.md`).
- La red es una versión reducida con tiempos y coordenadas aproximados.
