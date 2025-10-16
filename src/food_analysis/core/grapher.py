# =========================================================
# grapher.py
# =========================================================
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_activity_vs_leniency(
    user_stats: pd.DataFrame,
    log_x: bool = False,
    x_limit: int = None,
    jitter: float = 0.0,
) -> None:
    """
    Trace le scatter plot activité vs sévérité.

    Args:
        user_stats (pd.DataFrame): DataFrame avec 'n_ratings' et 'lenient_score'
        log_x (bool): appliquer log scale sur l'axe X
        x_limit (int): limite max de l'axe X (zoom sur petits/moyens utilisateurs)
        jitter (float): ajouter un jitter aléatoire sur Y pour disperser les points
    """
    df_plot = user_stats.dropna(subset=["n_ratings", "lenient_score"]).copy()
    df_plot = df_plot[df_plot["n_ratings"] > 0]

    # Appliquer jitter sur lenient_score si demandé
    if jitter > 0:
        np.random.seed(42)
        df_plot["lenient_score"] += np.random.uniform(
            -jitter, jitter, size=df_plot.shape[0]
        )

    plt.figure(figsize=(8, 6))
    plt.scatter(
        df_plot["n_ratings"],
        df_plot["lenient_score"],
        alpha=0.5,
        s=20,
        c=df_plot["lenient_score"],
        cmap="mako",
    )

    # Log scale sur X si demandé
    if log_x:
        plt.xscale("log")

    # Limite X si spécifiée
    if x_limit is not None:
        plt.xlim(0, x_limit)

    plt.colorbar(label="Leniency score")
    plt.title("Relation activité (n_ratings) vs sévérité (lenient_score)")
    plt.xlabel("Nombre de recettes notées (n_ratings)")
    plt.ylabel("Leniency score")
    plt.show()
