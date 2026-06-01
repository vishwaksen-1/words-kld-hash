from collections import Counter

import numpy as np


def byte_distribution(byte_data):
    total = len(byte_data)
    dist = np.zeros(256)
    if total == 0:
        return dist

    counts = Counter(byte_data)
    for b, count in counts.items():
        dist[b] = count / total

    return dist


def uniform_byte_distribution():
    return np.ones(256) / 256


def kl_divergence(P, Q, eps=1e-12):
    mask = P > 0
    P_nonzero = P[mask]
    Q_nonzero = np.clip(Q[mask], eps, 1)
    return float(np.sum(P_nonzero * np.log(P_nonzero / Q_nonzero)))


def shannon_entropy(P, eps=1e-12):
    P_nonzero = P[P > eps]
    return float(-np.sum(P_nonzero * np.log2(P_nonzero)))


def analyze_bytes(name, byte_data, plain_dist, uniform_dist, group=None, detail=None):
    dist = byte_distribution(byte_data)
    return {
        "group": group or "main",
        "name": name,
        "detail": detail or "",
        "bytes": len(byte_data),
        "entropy_bits": shannon_entropy(dist),
        "kl_to_uniform": kl_divergence(dist, uniform_dist),
        "kl_plain_to_method": kl_divergence(plain_dist, dist),
        "kl_method_to_plain": kl_divergence(dist, plain_dist),
        "distribution": dist,
    }


def ngram_counts(byte_data, n):
    if n < 1:
        raise ValueError("n must be >= 1")
    if len(byte_data) < n:
        return Counter()

    return Counter(byte_data[i:i + n] for i in range(len(byte_data) - n + 1))


def sparse_entropy_bits(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0

    probs = np.array(list(counts.values()), dtype=float) / total
    return float(-np.sum(probs * np.log2(probs)))


def sparse_kl_to_uniform(counts, support_size):
    total = sum(counts.values())
    if total == 0:
        return 0.0

    probs = np.array(list(counts.values()), dtype=float) / total
    return float(np.sum(probs * np.log(probs * support_size)))


def sparse_kl_divergence(P_counts, Q_counts, eps=1e-12):
    P_total = sum(P_counts.values())
    Q_total = sum(Q_counts.values())
    if P_total == 0:
        return 0.0
    if Q_total == 0:
        return float("inf")

    kl = 0.0
    for token, p_count in P_counts.items():
        p = p_count / P_total
        q = Q_counts.get(token, 0) / Q_total
        q = max(q, eps)
        kl += p * np.log(p / q)

    return float(kl)


def analyze_ngrams(name, byte_data, plain_counts, n, group=None, detail=None):
    counts = ngram_counts(byte_data, n)
    support_size = 256 ** n
    return {
        "group": group or "ngram",
        "name": name,
        "detail": detail or "",
        "bytes": len(byte_data),
        "ngram_n": n,
        "windows": sum(counts.values()),
        "unique_ngrams": len(counts),
        "entropy_bits": sparse_entropy_bits(counts),
        "max_entropy_bits": n * 8,
        "kl_to_uniform": sparse_kl_to_uniform(counts, support_size),
        "kl_plain_to_method": sparse_kl_divergence(plain_counts, counts),
        "kl_method_to_plain": sparse_kl_divergence(counts, plain_counts),
        "distribution": counts,
    }


def block_counts(byte_data, block_size, drop_partial=True):
    if block_size < 1:
        raise ValueError("block_size must be >= 1")

    usable = len(byte_data)
    if drop_partial:
        usable = (usable // block_size) * block_size

    counts = Counter(
        byte_data[i:i + block_size]
        for i in range(0, usable, block_size)
        if len(byte_data[i:i + block_size]) == block_size
    )
    return counts


def analyze_blocks(name, byte_data, block_size, group=None, detail=None):
    counts = block_counts(byte_data, block_size)
    total_blocks = sum(counts.values())
    repeated_blocks = sum(count - 1 for count in counts.values() if count > 1)
    repeated_kinds = sum(1 for count in counts.values() if count > 1)
    repeat_ratio = repeated_blocks / total_blocks if total_blocks else 0.0

    return {
        "group": group or "block-study",
        "name": name,
        "detail": detail or "",
        "bytes": len(byte_data),
        "block_size": block_size,
        "blocks": total_blocks,
        "unique_blocks": len(counts),
        "repeated_blocks": repeated_blocks,
        "repeated_block_kinds": repeated_kinds,
        "repeat_ratio": repeat_ratio,
        "entropy_bits": sparse_entropy_bits(counts),
        "max_entropy_bits": block_size * 8,
        "distribution": counts,
    }
