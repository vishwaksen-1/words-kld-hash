import csv
from pathlib import Path


RESULTS_DIR = Path("results")


def load_csv(name):
    with (RESULTS_DIR / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(value, digits=4):
    return f"{float(value):.{digits}f}"


def print_table(headers, rows):
    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        print("| " + " | ".join(row) + " |")


def post1_summary():
    plain = next(row for row in load_csv("cipher_ladder.csv") if row["name"] == "Plain")
    hash_rows = load_csv("hash_family.csv")
    selected = [plain] + hash_rows
    print("\n## Post 1: Plaintext vs Hash Family")
    print_table(
        ["Method", "Digest bytes", "Entropy bits/byte", "KL(method || uniform)"],
        [
            [
                row["name"],
                row.get("digest_bytes", ""),
                fnum(row["entropy_bits"]),
                fnum(row["kl_to_uniform"]),
            ]
            for row in selected
        ],
    )


def post2_summary():
    rows = load_csv("cipher_ladder.csv")
    names = ["Plain", "Caesar", "Columnar", "Substitution", "Vigenere", "XOR", "SHA-256"]
    selected = [next(row for row in rows if row["name"] == name) for name in names]
    print("\n## Post 2: Classical Cipher Ladder")
    print_table(
        ["Method", "Detail", "Entropy bits/byte", "KL(method || uniform)"],
        [
            [row["name"], row["detail"], fnum(row["entropy_bits"]), fnum(row["kl_to_uniform"])]
            for row in selected
        ],
    )


def post3_summary():
    rows = load_csv("ngram_window_study.csv")
    selected = [
        row for row in rows
        if row["name"] == "Columnar" and row["detail"] == "cols=8"
    ]
    print("\n## Post 3: Columnar Transposition Across Windows")
    print_table(
        ["Window", "Unique n-grams", "KL(Plain || Columnar)"],
        [
            [row["ngram_n"], row["unique_ngrams"], fnum(row["kl_plain_to_method"])]
            for row in selected
        ],
    )


def post4_summary():
    modern = load_csv("modern_cipher_modes.csv")
    mode_names = {
        ("AES-128", "ECB"),
        ("AES-128", "CBC"),
        ("AES-128", "CTR"),
        ("DES", "ECB"),
        ("DES", "CBC"),
        ("3DES", "ECB"),
        ("3DES", "CBC"),
    }
    selected = [row for row in modern if (row["name"], row["detail"]) in mode_names]

    print("\n## Post 4: Modern Modes Byte Metrics")
    print_table(
        ["Method", "Mode", "Entropy bits/byte", "KL(method || uniform)"],
        [
            [row["name"], row["detail"], fnum(row["entropy_bits"]), fnum(row["kl_to_uniform"])]
            for row in selected
        ],
    )

    ecb = load_csv("ecb_repeated_block_demo.csv")
    selected = [
        row for row in ecb
        if row["block_size"] == "16"
    ]
    print("\n## Post 4: Synthetic ECB Repeated-Block Demo")
    print_table(
        ["Method", "Mode", "Block size", "Repeated block ratio"],
        [
            [
                row["name"],
                row["detail"],
                row["block_size"],
                f"{100 * float(row['repeat_ratio']):.2f}%",
            ]
            for row in selected
        ],
    )


def main():
    post1_summary()
    post2_summary()
    post3_summary()
    post4_summary()


if __name__ == "__main__":
    main()
