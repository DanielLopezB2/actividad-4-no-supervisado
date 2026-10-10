"""Cluster station-days into demand archetypes: python -m src.cluster.

Features are the SHAPE of the hourly profile (hourly boardings as shares of the
day total) plus log total volume. No label is used for fitting; the hidden
archetype from src.dataset is used only to report external validation (ARI).
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.cluster import AgglomerativeClustering, KMeans  # noqa: E402
from sklearn.decomposition import PCA  # noqa: E402
from sklearn.metrics import adjusted_rand_score, silhouette_score  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from src.dataset import CSV_PATH, HOUR_COLUMNS, HOURS, ROOT, STATION_ARCHETYPE, generate_dataset  # noqa: E402

SEED = 42
K_RANGE = range(2, 9)
IMG_DIR = ROOT / "docs" / "img"


def load_data(path=CSV_PATH) -> pd.DataFrame:
    """Return the station-day table, generating the CSV first if it does not exist."""
    if not path.exists():
        generate_dataset().to_csv(path, index=False)
    return pd.read_csv(path)


def build_features(df: pd.DataFrame) -> np.ndarray:
    """Standardized [hourly shares..., log total volume] matrix, one row per station-day."""
    counts = df[HOUR_COLUMNS].to_numpy(dtype=float)
    total = counts.sum(axis=1, keepdims=True)
    return StandardScaler().fit_transform(np.hstack([counts / total, np.log(total)]))


def fit_kmeans(X: np.ndarray, k: int) -> KMeans:
    return KMeans(n_clusters=k, n_init=10, random_state=SEED).fit(X)


def fit_hierarchical(X: np.ndarray, k: int) -> np.ndarray:
    """Ward-linkage agglomerative labels."""
    return AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(X)


def choose_k(X: np.ndarray, k_range=K_RANGE) -> tuple:
    """Return (best k by silhouette, {k: silhouette})."""
    scores = {k: silhouette_score(X, fit_kmeans(X, k).labels_) for k in k_range}
    return max(scores, key=scores.get), scores


def _save_plots(df, X, labels, k) -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    pca = PCA(n_components=2, random_state=SEED)
    xy = pca.fit_transform(X)
    fig, ax = plt.subplots(figsize=(7, 5))
    scatter = ax.scatter(xy[:, 0], xy[:, 1], c=labels, cmap="tab10", s=10)
    ax.legend(*scatter.legend_elements(), title="Cluster")
    ax.set_xlabel(f"Componente 1 ({pca.explained_variance_ratio_[0]:.0%} de la varianza)")
    ax.set_ylabel(f"Componente 2 ({pca.explained_variance_ratio_[1]:.0%} de la varianza)")
    ax.set_title(f"Estación-día en el plano PCA (KMeans, k={k})")
    fig.savefig(IMG_DIR / "clusters-pca.png", dpi=110, bbox_inches="tight")
    plt.close(fig)

    shares = df[HOUR_COLUMNS].div(df[HOUR_COLUMNS].sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(7, 5))
    for c in range(k):
        ax.plot(HOURS, shares[labels == c].mean(), marker="o", label=f"Cluster {c}")
    ax.set_xlabel("Hora del día")
    ax.set_ylabel("Proporción de abordajes del día")
    ax.set_title("Perfil horario medio por cluster")
    ax.legend()
    fig.savefig(IMG_DIR / "perfiles-cluster.png", dpi=110, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    df = load_data()
    X = build_features(df)
    k, scores = choose_k(X)
    print(f"Rows: {len(df)} | features: {X.shape[1]}")
    print("Silhouette by k (KMeans):")
    for kk, s in scores.items():
        print(f"  k={kk}: {s:.3f}{'  <- chosen' if kk == k else ''}")

    labels = fit_kmeans(X, k).labels_
    hier = fit_hierarchical(X, k)
    truth = df["station"].map(STATION_ARCHETYPE)  # validation only, never used for fitting
    print(f"\nARI KMeans vs hierarchical:        {adjusted_rand_score(labels, hier):.3f}")
    print(f"ARI KMeans vs hidden archetype:    {adjusted_rand_score(truth, labels):.3f}  (validation only)")
    print(f"ARI hierarchical vs archetype:     {adjusted_rand_score(truth, hier):.3f}  (validation only)")

    for c in range(k):
        rows = df[labels == c]
        days = rows["day_type"].value_counts(normalize=True).round(2).to_dict()
        top = rows["station"].value_counts().head(5).to_dict()
        print(f"\nCluster {c}: {len(rows)} station-days | mean total {rows[HOUR_COLUMNS].sum(axis=1).mean():.0f}")
        print(f"  day types: {days}\n  top stations: {top}")

    _save_plots(df, X, labels, k)
    print(f"\nPlots saved to {IMG_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
