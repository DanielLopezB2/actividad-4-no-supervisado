import pandas as pd

from src.dataset import DAY_TYPES, HOUR_COLUMNS, N_DAYS, STATION_ARCHETYPE, generate_dataset, station_names


def test_shape_and_columns():
    df = generate_dataset()
    assert len(df) == len(station_names()) * N_DAYS
    assert list(df.columns) == ["station", "day_type", "rain"] + HOUR_COLUMNS


def test_no_nulls_and_valid_values():
    df = generate_dataset()
    assert not df.isna().any().any()
    assert set(df["day_type"]) <= set(DAY_TYPES)
    assert set(df["rain"]) <= {0, 1}
    assert (df[HOUR_COLUMNS] >= 0).all().all()
    assert all(pd.api.types.is_integer_dtype(df[c]) for c in HOUR_COLUMNS)


def test_all_network_stations_have_an_archetype():
    assert set(station_names()) == set(STATION_ARCHETYPE)


def test_seed_reproducibility():
    pd.testing.assert_frame_equal(generate_dataset(seed=7), generate_dataset(seed=7))
    assert not generate_dataset(seed=7).equals(generate_dataset(seed=8))


def test_archetype_is_not_leaked_into_the_data():
    assert "archetype" not in generate_dataset().columns
