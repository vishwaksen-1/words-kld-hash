from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_byte_distributions(results, uniform_dist, output_path, max_items=12):
    selected = results[:max_items]
    cols = 2
    rows = int(np.ceil(len(selected) / cols))
    x = np.arange(256)

    fig, axes = plt.subplots(rows, cols, figsize=(14, 3.1 * rows), sharex=True, sharey=True)
    axes = np.atleast_1d(axes).ravel()

    for ax, result in zip(axes, selected):
        ax.bar(x, result["distribution"], width=1.0, alpha=0.85)
        ax.axhline(uniform_dist[0], color="black", linewidth=1, linestyle="--")
        title = result["name"]
        if result["detail"]:
            title = f"{title} ({result['detail']})"
        ax.set_title(title)
        ax.set_ylabel("Probability")
        ax.set_xlim(0, 255)
        ax.grid(axis="y", alpha=0.25)

    for ax in axes[len(selected):]:
        ax.axis("off")

    for ax in axes[-cols:]:
        ax.set_xlabel("Byte value")

    fig.suptitle("Empirical Byte Distributions vs Uniform", y=0.995)
    fig.tight_layout()
    _save(fig, output_path)


def plot_metric_bars(results, metric, output_path, title, ylabel):
    labels = [_label(row) for row in results]
    values = [row[metric] for row in results]

    fig, ax = plt.subplots(figsize=(max(10, len(results) * 0.85), 5.5))
    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=35, labelsize=9)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    _save(fig, output_path)


def plot_study_lines(
    rows,
    output_path,
    title,
    x_field="key_length",
    series_field="key_type",
    y_field="kl_to_uniform",
    ylabel="KL(cipher || uniform)",
):
    groups = {}
    for row in rows:
        groups.setdefault(row[series_field], []).append(row)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for label, group_rows in groups.items():
        group_rows = sorted(group_rows, key=lambda row: row[x_field])
        ax.plot(
            [row[x_field] for row in group_rows],
            [row[y_field] for row in group_rows],
            marker="o",
            label=label,
        )

    ax.set_title(title)
    ax.set_xlabel(x_field.replace("_", " ").title())
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    _save(fig, output_path)


def _label(row):
    if row["detail"]:
        return f"{row['name']} {row['detail']}"
    return row["name"]


def _save(fig, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
