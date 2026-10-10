import numpy as np
import pytest
from sklearn.metrics import adjusted_rand_score, silhouette_score

from src import cluster
from src.dataset import HOUR_COLUMNS, STATION_ARCHETYPE, generate_dataset


@pytest.fixture(scope="module")
def df():
    return generate_dataset()


@pytest.fixture(scope="module")
def X(df):
    return cluster.build_features(df)


@pytest.fixture(scope="module")
def chosen(X):
    return cluster.choose_k(X)


def test_features_have_no_nan_and_expected_width(df, X):
    assert not np.isnan(X).any()
    assert X.shape == (len(df), len(HOUR_COLUMNS) + 1)


def test_hourly_shares_sum_to_one(df):
    counts = df[HOUR_COLUMNS].to_numpy(dtype=float)
    assert np.allclose((counts / counts.sum(axis=1, keepdims=True)).sum(axis=1), 1.0)


def test_choose_k_returns_k_in_range(chosen):
    k, scores = chosen
    assert k in cluster.K_RANGE
    assert set(scores) == set(cluster.K_RANGE)
    assert scores[k] == max(scores.values())


def test_kmeans_beats_random_labels_on_silhouette(X, chosen):
    k, _ = chosen
    labels = cluster.fit_kmeans(X, k).labels_
    random_labels = np.random.default_rng(0).integers(0, k, len(X))
    assert silhouette_score(X, labels) > silhouette_score(X, random_labels) + 0.1


def test_kmeans_recovers_hidden_archetypes(df, X, chosen):
    k, _ = chosen
    labels = cluster.fit_kmeans(X, k).labels_
    assert adjusted_rand_score(df["station"].map(STATION_ARCHETYPE), labels) > 0.6


def test_hierarchical_agrees_with_kmeans(X, chosen):
    k, _ = chosen
    kmeans = cluster.fit_kmeans(X, k).labels_
    assert adjusted_rand_score(kmeans, cluster.fit_hierarchical(X, k)) > 0.6
