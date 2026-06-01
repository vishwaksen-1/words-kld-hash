import random

from kldcrypto.ciphers import (
    caesar_shift,
    columnar_transposition,
    hash_each_word,
    identity,
    random_ascii_key,
    random_byte_key,
    sha256_each_word,
    substitution_cipher,
    vigenere_encrypt,
    xor_repeating_key,
)
from kldcrypto.data import load_words, word_key, words_to_bytes
from kldcrypto.metrics import (
    analyze_bytes,
    analyze_blocks,
    analyze_ngrams,
    byte_distribution,
    ngram_counts,
    uniform_byte_distribution,
)
from kldcrypto.modern import aes_encrypt, des_encrypt, triple_des_encrypt
from kldcrypto.reporting import ensure_dirs, print_block_table, print_ngram_table, print_table, write_csv
from kldcrypto.visualize import plot_byte_distributions, plot_metric_bars, plot_study_lines


RANDOM_SEED = 20260529
WORDLIST_PATH = "wordlist.txt"
RESULTS_DIR = "results"
PLOTS_DIR = "plots"
NGRAM_SIZES = [1, 2, 3, 4, 8]
MODERN_NGRAM_SIZES = [1, 2, 3, 4]
BLOCK_SIZES = [8, 16]
HASH_ALGORITHMS = [
    ("DJB2", "32-bit non-crypto", "djb2"),
    ("CRC-24", "24-bit checksum", "crc24"),
    ("MD5", "128-bit broken crypto", "md5"),
    ("SHA-1", "160-bit broken crypto", "sha1"),
    ("SHA-256", "256-bit", "sha256"),
    ("SHA-512", "512-bit", "sha512"),
]


def analyze_named_bytes(named_items, plain_dist, uniform_dist, group):
    return [
        analyze_bytes(name, data, plain_dist, uniform_dist, group=group, detail=detail)
        for name, detail, data in named_items
    ]


def resize_key(key, length):
    if len(key) >= length:
        return key[:length]
    repeats = (length // len(key)) + 1
    return (key * repeats)[:length]


def first_word_key_at_least(words, length):
    for word in words:
        key = word.encode("utf-8")
        if len(key) >= length:
            return key[:length]
    return resize_key(words[-1].encode("utf-8"), length)


def build_main_ladder(words, plaintext):
    return [
        ("Plain", "", plaintext),
        ("Identity", "", identity(plaintext)),
        ("Caesar", "shift=3", caesar_shift(plaintext, shift=3)),
        ("Vigenere", "key=lemon", vigenere_encrypt(plaintext, b"lemon")),
        ("Columnar", "cols=8", columnar_transposition(plaintext, columns=8)),
        ("Substitution", "sha-keyed", substitution_cipher(plaintext, key=b"classical-substitution")),
        ("XOR", "key=lemon", xor_repeating_key(plaintext, b"lemon")),
        ("SHA-256", "per word", sha256_each_word(words)),
    ]


def build_hash_outputs(words):
    return [
        (name, detail, hash_each_word(words, algorithm))
        for name, detail, algorithm in HASH_ALGORITHMS
    ]


def hash_family_study(hash_items, plain_dist, uniform_dist, word_count):
    rows = analyze_named_bytes(hash_items, plain_dist, uniform_dist, group="hash-family")
    digest_lengths = {
        name: len(data) // word_count
        for name, _, data in hash_items
    }
    for row in rows:
        row["digest_bytes"] = digest_lengths[row["name"]]
        row["digest_bits"] = row["digest_bytes"] * 8
    return rows


def vigenere_key_study(plaintext, words, plain_dist, uniform_dist, rng):
    lengths = [1, 2, 3, 5, 8, 13, 21, 34]
    rows = []

    for length in lengths:
        known_key = first_word_key_at_least(words, length)
        random_word = resize_key(word_key(words, rng.randrange(len(words))), length)

        key_variants = [
            ("known-word", known_key),
            ("random-word", random_word),
            ("random-ascii", random_ascii_key(length, rng)),
            ("random-bytes", random_byte_key(length, rng)),
        ]

        for key_type, key in key_variants:
            ciphertext = vigenere_encrypt(plaintext, key)
            row = analyze_bytes(
                "Vigenere",
                ciphertext,
                plain_dist,
                uniform_dist,
                group="vigenere-study",
                detail=f"{key_type}, n={length}",
            )
            row["key_type"] = key_type
            row["key_length"] = length
            row["key_hex"] = key.hex()
            rows.append(row)

    return rows


def columnar_key_study(plaintext, plain_dist, uniform_dist):
    columns_to_test = [2, 3, 4, 5, 8, 12, 16, 24, 32, 48]
    rows = []

    for columns in columns_to_test:
        ciphertext = columnar_transposition(plaintext, columns=columns)
        row = analyze_bytes(
            "Columnar",
            ciphertext,
            plain_dist,
            uniform_dist,
            group="columnar-study",
            detail=f"cols={columns}",
        )
        row["key_type"] = "columns"
        row["key_length"] = columns
        rows.append(row)

    return rows


def xor_key_study(plaintext, words, plain_dist, uniform_dist, rng):
    lengths = [1, 2, 3, 5, 8, 13, 21, 34]
    rows = []

    for length in lengths:
        known_key = first_word_key_at_least(words, length)
        random_word = resize_key(word_key(words, rng.randrange(len(words))), length)

        key_variants = [
            ("known-word", known_key),
            ("random-word", random_word),
            ("random-ascii", random_ascii_key(length, rng)),
            ("random-bytes", random_byte_key(length, rng)),
        ]

        for key_type, key in key_variants:
            ciphertext = xor_repeating_key(plaintext, key)
            row = analyze_bytes(
                "XOR",
                ciphertext,
                plain_dist,
                uniform_dist,
                group="xor-study",
                detail=f"{key_type}, n={length}",
            )
            row["key_type"] = key_type
            row["key_length"] = length
            row["key_hex"] = key.hex()
            rows.append(row)

    return rows


def ngram_window_study(ladder_items, plaintext):
    rows = []
    plain_counts_by_n = {
        n: ngram_counts(plaintext, n)
        for n in NGRAM_SIZES
    }

    for n in NGRAM_SIZES:
        for name, detail, data in ladder_items:
            row = analyze_ngrams(
                name,
                data,
                plain_counts_by_n[n],
                n,
                group="ngram-study",
                detail=detail,
            )
            rows.append(row)

    return rows


def build_modern_cipher_outputs(plaintext):
    rows = []

    for key_size in [128, 256]:
        for mode_name in ["ECB", "CBC", "CTR", "CFB", "OFB"]:
            rows.append((
                f"AES-{key_size}",
                mode_name,
                aes_encrypt(plaintext, mode_name, key_size=key_size),
            ))

    for mode_name in ["ECB", "CBC", "CFB", "OFB"]:
        rows.append((
            "DES",
            mode_name,
            des_encrypt(plaintext, mode_name),
        ))

    for mode_name in ["ECB", "CBC", "CFB", "OFB"]:
        rows.append((
            "3DES",
            mode_name,
            triple_des_encrypt(plaintext, mode_name),
        ))

    return rows


def build_ecb_leakage_demo_outputs():
    pattern_plaintext = (
        b"YELLOW SUBMARINE" * 1024
        + b"REPEATED-BLOCK!!" * 1024
    )

    return [
        ("Pattern Plain", "repeated blocks", pattern_plaintext),
        ("AES-128", "ECB", aes_encrypt(pattern_plaintext, "ECB", key_size=128)),
        ("AES-128", "CBC", aes_encrypt(pattern_plaintext, "CBC", key_size=128)),
        ("AES-128", "CTR", aes_encrypt(pattern_plaintext, "CTR", key_size=128)),
        ("DES", "ECB", des_encrypt(pattern_plaintext, "ECB")),
        ("DES", "CBC", des_encrypt(pattern_plaintext, "CBC")),
        ("3DES", "ECB", triple_des_encrypt(pattern_plaintext, "ECB")),
        ("3DES", "CBC", triple_des_encrypt(pattern_plaintext, "CBC")),
    ]


def modern_cipher_study(modern_items, plain_dist, uniform_dist):
    return analyze_named_bytes(modern_items, plain_dist, uniform_dist, group="modern-cipher")


def block_repetition_study(named_items):
    rows = []
    for block_size in BLOCK_SIZES:
        for name, detail, data in named_items:
            row = analyze_blocks(
                name,
                data,
                block_size,
                group="block-study",
                detail=detail,
            )
            row["series"] = f"{name} {detail}".strip()
            rows.append(row)
    return rows


def ecb_leakage_block_study(ecb_demo_items):
    rows = []
    for block_size in BLOCK_SIZES:
        for name, detail, data in ecb_demo_items:
            row = analyze_blocks(
                name,
                data,
                block_size,
                group="ecb-demo",
                detail=detail,
            )
            row["series"] = f"{name} {detail}".strip()
            rows.append(row)
    return rows


def modern_ngram_study(modern_items, plaintext):
    rows = []
    plain_counts_by_n = {
        n: ngram_counts(plaintext, n)
        for n in MODERN_NGRAM_SIZES
    }

    for n in MODERN_NGRAM_SIZES:
        for name, detail, data in modern_items:
            row = analyze_ngrams(
                name,
                data,
                plain_counts_by_n[n],
                n,
                group="modern-ngram",
                detail=detail,
            )
            row["series"] = f"{name} {detail}".strip()
            rows.append(row)

    return rows


def print_interpretation():
    print("\nInterpretation notes")
    print("- Caesar and substitution relabel bytes, so byte entropy is preserved.")
    print("- Columnar transposition reorders bytes only, so byte-frequency KL is unchanged.")
    print("- Bigram/trigram/window KL can expose positional disruption that unigram KL misses.")
    print("- Wider windows have enormous supports, so KL-to-uniform grows unless outputs are very sample-rich.")
    print("- Vigenere and XOR can flatten byte frequencies when repeated keys mix symbols across byte classes.")
    print("- Short digest hashes/checksums have less output data, so KL estimates are noisier.")
    print("- SHA-256 is included as the intro benchmark: close to uniform at byte level, not a security proof.")
    print("- ECB can look random by byte KL while still leaking repeated block structure.")
    print("- The repeated-block demo is intentionally synthetic; it isolates the mode-of-operation failure.")
    print("- DES is included as a legacy comparison; 3DES is included as the DES-family bridge still exposed by cryptography.")


def main():
    ensure_dirs(RESULTS_DIR, PLOTS_DIR)
    rng = random.Random(RANDOM_SEED)

    words = load_words(WORDLIST_PATH)
    plaintext = words_to_bytes(words)
    plain_dist = byte_distribution(plaintext)
    uniform_dist = uniform_byte_distribution()

    ladder_items = build_main_ladder(words, plaintext)
    hash_items = build_hash_outputs(words)
    modern_items = build_modern_cipher_outputs(plaintext)
    ecb_demo_items = build_ecb_leakage_demo_outputs()
    block_items = ladder_items + modern_items
    ladder_results = analyze_named_bytes(ladder_items, plain_dist, uniform_dist, group="cipher-ladder")
    hash_rows = hash_family_study(hash_items, plain_dist, uniform_dist, len(words))
    modern_results = modern_cipher_study(modern_items, plain_dist, uniform_dist)

    vigenere_rows = vigenere_key_study(plaintext, words, plain_dist, uniform_dist, rng)
    columnar_rows = columnar_key_study(plaintext, plain_dist, uniform_dist)
    xor_rows = xor_key_study(plaintext, words, plain_dist, uniform_dist, rng)
    ngram_rows = ngram_window_study(ladder_items, plaintext)
    modern_ngram_rows = modern_ngram_study(modern_items, plaintext)
    block_rows = block_repetition_study(block_items)
    ecb_demo_block_rows = ecb_leakage_block_study(ecb_demo_items)

    print(f"Loaded words: {len(words)}")
    print(f"Plaintext bytes: {len(plaintext)}")
    print_table(ladder_results, title="Ancient-to-modern transformation ladder")
    print_table(hash_rows, title="Hash family comparison")
    print_table(modern_results, title="Modern cipher mode comparison")
    print_table(vigenere_rows, title="Vigenere KLD vs key length/randomness")
    print_table(columnar_rows, title="Columnar transposition KLD vs columns")
    print_table(xor_rows, title="XOR KLD vs key length/randomness")
    print_ngram_table(ngram_rows, title="Sliding window n-gram KLD analysis")
    print_ngram_table(modern_ngram_rows, title="Modern cipher n-gram KLD analysis")
    print_block_table(block_rows, title="Block repetition analysis")
    print_block_table(ecb_demo_block_rows, title="Synthetic ECB repeated-block leakage demo")
    print_interpretation()

    write_csv(ladder_results, f"{RESULTS_DIR}/cipher_ladder.csv")
    write_csv(hash_rows, f"{RESULTS_DIR}/hash_family.csv")
    write_csv(modern_results, f"{RESULTS_DIR}/modern_cipher_modes.csv")
    write_csv(vigenere_rows, f"{RESULTS_DIR}/vigenere_key_study.csv")
    write_csv(columnar_rows, f"{RESULTS_DIR}/columnar_key_study.csv")
    write_csv(xor_rows, f"{RESULTS_DIR}/xor_key_study.csv")
    write_csv(ngram_rows, f"{RESULTS_DIR}/ngram_window_study.csv")
    write_csv(modern_ngram_rows, f"{RESULTS_DIR}/modern_ngram_study.csv")
    write_csv(block_rows, f"{RESULTS_DIR}/block_repetition_study.csv")
    write_csv(ecb_demo_block_rows, f"{RESULTS_DIR}/ecb_repeated_block_demo.csv")

    plot_byte_distributions(
        ladder_results,
        uniform_dist,
        f"{PLOTS_DIR}/cipher_ladder_byte_distributions.png",
        max_items=len(ladder_results),
    )
    plot_metric_bars(
        ladder_results,
        "kl_to_uniform",
        f"{PLOTS_DIR}/cipher_ladder_kl_to_uniform.png",
        "KL Divergence to Uniform by Method",
        "KL(method || uniform)",
    )
    plot_metric_bars(
        ladder_results,
        "entropy_bits",
        f"{PLOTS_DIR}/cipher_ladder_entropy.png",
        "Byte Entropy by Method",
        "Entropy (bits)",
    )
    plot_metric_bars(
        hash_rows,
        "kl_to_uniform",
        f"{PLOTS_DIR}/hash_family_kl_to_uniform.png",
        "Hash Family: KL Divergence to Uniform",
        "KL(hash output || uniform)",
    )
    plot_metric_bars(
        hash_rows,
        "entropy_bits",
        f"{PLOTS_DIR}/hash_family_entropy.png",
        "Hash Family: Byte Entropy",
        "Entropy (bits)",
    )
    plot_metric_bars(
        modern_results,
        "kl_to_uniform",
        f"{PLOTS_DIR}/modern_modes_kl_to_uniform.png",
        "Modern Cipher Modes: KL Divergence to Uniform",
        "KL(method || uniform)",
    )
    plot_metric_bars(
        modern_results,
        "entropy_bits",
        f"{PLOTS_DIR}/modern_modes_entropy.png",
        "Modern Cipher Modes: Byte Entropy",
        "Entropy (bits)",
    )
    plot_study_lines(
        vigenere_rows,
        f"{PLOTS_DIR}/vigenere_keylength_kl.png",
        "Vigenere: KL to Uniform vs Key Length",
    )
    plot_study_lines(
        columnar_rows,
        f"{PLOTS_DIR}/columnar_columns_kl.png",
        "Columnar Transposition: KL to Uniform vs Columns",
    )
    plot_study_lines(
        xor_rows,
        f"{PLOTS_DIR}/xor_keylength_kl.png",
        "XOR: KL to Uniform vs Key Length",
    )
    plot_study_lines(
        ngram_rows,
        f"{PLOTS_DIR}/ngram_kl_to_uniform.png",
        "Sliding Windows: KL to Uniform vs Window Size",
        x_field="ngram_n",
        series_field="name",
        ylabel="KL(n-gram distribution || uniform)",
    )
    plot_study_lines(
        ngram_rows,
        f"{PLOTS_DIR}/ngram_entropy.png",
        "Sliding Windows: Entropy vs Window Size",
        x_field="ngram_n",
        series_field="name",
        y_field="entropy_bits",
        ylabel="Entropy (bits)",
    )
    plot_study_lines(
        modern_ngram_rows,
        f"{PLOTS_DIR}/modern_ngram_kl_to_uniform.png",
        "Modern Cipher Modes: KL to Uniform vs Window Size",
        x_field="ngram_n",
        series_field="series",
        ylabel="KL(n-gram distribution || uniform)",
    )
    plot_study_lines(
        block_rows,
        f"{PLOTS_DIR}/block_repeat_ratio.png",
        "Repeated Block Ratio by Block Size",
        x_field="block_size",
        series_field="series",
        y_field="repeat_ratio",
        ylabel="Repeated block ratio",
    )
    plot_study_lines(
        ecb_demo_block_rows,
        f"{PLOTS_DIR}/ecb_repeated_block_demo.png",
        "Synthetic ECB Demo: Repeated Block Ratio",
        x_field="block_size",
        series_field="series",
        y_field="repeat_ratio",
        ylabel="Repeated block ratio",
    )

    print(f"\nSaved CSV files in: {RESULTS_DIR}/")
    print(f"Saved plots in: {PLOTS_DIR}/")


if __name__ == "__main__":
    main()
