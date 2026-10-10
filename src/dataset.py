"""Synthetic station-day demand profiles: python -m src.dataset [-> data/station_profiles.csv].

IMPORTANT: this data is SYNTHETIC. It is generated from the stated assumptions
below, NOT from real TransMilenio measurements. The shapes and volumes are
plausible guesses for academic use; a clustering model trained on this data only
recovers the archetypes written here (plus noise), not real passenger behavior.

Each row is one station-day: hourly boardings h05..h22 for one station.

    boardings[h] ~ Poisson(base_volume * shape[archetype][h] * day_factor
                           * rain_factor * lognormal_noise)

Archetype shapes are OUR assumptions, tuned so the four archetypes are visibly
different: residential (morning peak), business (evening peak + midday plateau),
hub (high volume, three peaks: both rush hours and midday transfers) and mixed
(low volume, one broad late-morning/afternoon bump). Separating hub from mixed
was done by tuning these assumptions, so a perfect recovery shows the method
works on well-separated groups, not that real stations behave this way.

The archetype of each station is a hidden ground truth: it is NEVER written to
the CSV and is only used to validate the clusters, not to fit them.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
NETWORK_PATH = ROOT / "data" / "network.json"
CSV_PATH = ROOT / "data" / "station_profiles.csv"

HOURS = list(range(5, 23))
HOUR_COLUMNS = [f"h{h:02d}" for h in HOURS]
DAY_TYPES = ["weekday", "saturday", "sunday_holiday"]
DAY_TYPE_PROBS = [0.6, 0.2, 0.2]
DAY_FACTOR = {"weekday": 1.0, "saturday": 0.7, "sunday_holiday": 0.45}
RAIN_PROB = 0.25
RAIN_FACTOR = 1.1
NOISE_SIGMA = 0.12  # sigma of the lognormal day-level multiplier
N_DAYS = 60  # observed days per station
SEED = 42

# Hidden ground truth (validation only).
ARCHETYPES = {
    "residential": ["Portal Eldorado", "Portal Américas", "Banderas", "Marsella", "Modelia", "Normandía"],
    "business": ["Calle 100", "Calle 72", "Calle 63", "Calle 45", "Calle 34", "Héroes", "Calle 75"],
    "hub": ["Calle 26", "Centro Memoria", "Ricaurte"],
    "mixed": ["Av. Rojas", "Corferias", "Concejo de Bogotá", "Puente Aranda"],
}
STATION_ARCHETYPE = {s: a for a, stations in ARCHETYPES.items() for s in stations}
BASE_VOLUME = {"residential": 140, "business": 120, "hub": 260, "mixed": 70}  # boardings per hour


def _bump(center: float, width: float, height: float) -> np.ndarray:
    return height * np.exp(-0.5 * ((np.array(HOURS) - center) / width) ** 2)


# Relative hourly shape per archetype (arbitrary units, 1.0 = baseline).
SHAPES = {
    "residential": 0.25 + _bump(7, 1.2, 2.6) + _bump(18, 1.5, 0.5),  # strong morning departure peak
    "business": 0.3 + _bump(18, 1.2, 2.4) + _bump(13, 2.5, 0.7),  # strong evening peak, midday plateau
    "hub": 0.35 + _bump(7.5, 1.1, 1.5) + _bump(12.5, 1.8, 1.6) + _bump(17.5, 1.1, 1.5),  # high volume, three peaks (both rush hours + midday transfers)
    "mixed": 0.25 + _bump(11, 2.0, 1.2) + _bump(15, 2.2, 1.0),  # low volume, single broad late-morning/afternoon bump, no rush-hour peaks
}


def station_names(network_path: Path = NETWORK_PATH) -> list:
    """Station names in the order they appear in network.json."""
    network = json.loads(Path(network_path).read_text(encoding="utf-8"))
    return [s["name"] for s in network["stations"]]


def generate_dataset(n_days: int = N_DAYS, seed: int = SEED, network_path: Path = NETWORK_PATH) -> pd.DataFrame:
    """Return len(stations) * n_days station-day rows (no archetype column)."""
    rng = np.random.default_rng(seed)
    rows = []
    for station in station_names(network_path):
        archetype = STATION_ARCHETYPE[station]
        for _ in range(n_days):
            day_type = rng.choice(DAY_TYPES, p=DAY_TYPE_PROBS)
            rain = int(rng.random() < RAIN_PROB)
            level = (
                BASE_VOLUME[archetype]
                * DAY_FACTOR[day_type]
                * (RAIN_FACTOR if rain else 1.0)
                * rng.lognormal(0.0, NOISE_SIGMA)
            )
            counts = rng.poisson(level * SHAPES[archetype])
            rows.append({"station": station, "day_type": day_type, "rain": rain, **dict(zip(HOUR_COLUMNS, counts))})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    data = generate_dataset()
    data.to_csv(CSV_PATH, index=False)
    print(f"Wrote {len(data)} rows x {data.shape[1]} columns to {CSV_PATH.relative_to(ROOT)}")
    print(data["day_type"].value_counts(normalize=True).round(3).to_string())
    print(f"rain share: {data['rain'].mean():.3f}")
    print(data[HOUR_COLUMNS].sum(axis=1).describe().round(1).to_string())
