import hashlib
import numpy as np
from collections import Counter

# ---------- Helper functions ----------

def byte_distribution(byte_data):
    total = len(byte_data)
    counts = Counter(byte_data)
    
    dist = np.zeros(256)
    for b in range(256):
        dist[b] = counts[b] / total if total > 0 else 0
    
    return dist

def kl_divergence(P, Q, eps=1e-12):
    # avoid log(0)
    P = np.clip(P, eps, 1)
    Q = np.clip(Q, eps, 1)
    return np.sum(P * np.log(P / Q))

# ---------- Load wordlist ----------

def load_words(file_path):
    with open(file_path, 'r') as f:
        words = [line.strip() for line in f if line.strip()]
    return words

# ---------- Build datasets ----------

def words_to_bytes(words):
    return b''.join([w.encode('utf-8') for w in words])

def hash_words(words):
    hashed = []
    for w in words:
        h = hashlib.sha256(w.encode('utf-8')).digest()
        hashed.append(h)
    return b''.join(hashed)

# ---------- Main ----------

words = load_words("wordlist.txt")

# Dataset A: original
bytes_plain = words_to_bytes(words)

# Dataset B: hashed
bytes_hash = hash_words(words)

# Distributions
P = byte_distribution(bytes_plain)
Q = byte_distribution(bytes_hash)

# Uniform distribution
U = np.ones(256) / 256

# KL computations
kl_plain_uniform = kl_divergence(P, U)
kl_hash_uniform = kl_divergence(Q, U)
kl_plain_hash = kl_divergence(P, Q)

# ---------- Output ----------

print("KL(Plain || Uniform):", kl_plain_uniform)
print("KL(Hash  || Uniform):", kl_hash_uniform)
print("KL(Plain || Hash):   ", kl_plain_hash)