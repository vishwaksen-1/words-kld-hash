import csv
from pathlib import Path


SUMMARY_FIELDS = [
    "group",
    "name",
    "detail",
    "bytes",
    "ngram_n",
    "windows",
    "unique_ngrams",
    "block_size",
    "blocks",
    "unique_blocks",
    "repeated_blocks",
    "repeated_block_kinds",
    "repeat_ratio",
    "entropy_bits",
    "max_entropy_bits",
    "kl_to_uniform",
    "kl_plain_to_method",
    "kl_method_to_plain",
]


def ensure_dirs(*paths):
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def printable_rows(results):
    return [{field: row[field] for field in SUMMARY_FIELDS} for row in results]


def print_table(results, title=None):
    if title:
        print(f"\n{title}")

    header = (
        f"{'Group':<16}"
        f"{'Method':<18}"
        f"{'Detail':<24}"
        f"{'Bytes':>10}"
        f"{'Entropy':>12}"
        f"{'KL(||U)':>12}"
        f"{'KL(P||M)':>12}"
        f"{'KL(M||P)':>12}"
    )
    print(header)
    print("-" * len(header))

    for row in results:
        print(
            f"{row['group']:<16}"
            f"{row['name']:<18}"
            f"{row['detail']:<24}"
            f"{row['bytes']:>10}"
            f"{row['entropy_bits']:>12.6f}"
            f"{row['kl_to_uniform']:>12.6f}"
            f"{row['kl_plain_to_method']:>12.6f}"
            f"{row['kl_method_to_plain']:>12.6f}"
        )


def print_ngram_table(results, title=None):
    if title:
        print(f"\n{title}")

    header = (
        f"{'Method':<18}"
        f"{'Detail':<18}"
        f"{'n':>4}"
        f"{'Windows':>10}"
        f"{'Unique':>10}"
        f"{'Entropy':>12}"
        f"{'Max H':>10}"
        f"{'KL(||U)':>12}"
        f"{'KL(P||M)':>12}"
    )
    print(header)
    print("-" * len(header))

    for row in results:
        print(
            f"{row['name']:<18}"
            f"{row['detail']:<18}"
            f"{row['ngram_n']:>4}"
            f"{row['windows']:>10}"
            f"{row['unique_ngrams']:>10}"
            f"{row['entropy_bits']:>12.6f}"
            f"{row['max_entropy_bits']:>10.2f}"
            f"{row['kl_to_uniform']:>12.6f}"
            f"{row['kl_plain_to_method']:>12.6f}"
        )


def print_block_table(results, title=None):
    if title:
        print(f"\n{title}")

    header = (
        f"{'Group':<15}"
        f"{'Method':<18}"
        f"{'Detail':<18}"
        f"{'Block':>7}"
        f"{'Blocks':>9}"
        f"{'Unique':>9}"
        f"{'Repeated':>10}"
        f"{'Repeat %':>10}"
        f"{'Entropy':>12}"
    )
    print(header)
    print("-" * len(header))

    for row in results:
        print(
            f"{row['group']:<15}"
            f"{row['name']:<18}"
            f"{row['detail']:<18}"
            f"{row['block_size']:>7}"
            f"{row['blocks']:>9}"
            f"{row['unique_blocks']:>9}"
            f"{row['repeated_blocks']:>10}"
            f"{100 * row['repeat_ratio']:>9.3f}%"
            f"{row['entropy_bits']:>12.6f}"
        )


def write_csv(results, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(SUMMARY_FIELDS)
    for row in results:
        for field in row:
            if field != "distribution" and field not in fieldnames:
                fieldnames.append(field)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
