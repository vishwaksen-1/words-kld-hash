---
title: AES, DES, ECB, CBC: When Random-Looking Bytes Still Leak Structure
tags: cryptography, aes, block-ciphers, kl-divergence
---

# AES, DES, ECB, CBC: When Random-Looking Bytes Still Leak Structure

This is Part 4 of the KL divergence experiment series. The earlier posts showed that hashes and some encryption outputs can look close to uniform at the byte level, while weak classical ciphers often preserve visible structure.

This post moves to modern block ciphers and modes of operation. The main result is the classic ECB lesson in measured form: byte KL can say the output looks random-like while block repetition still leaks structure.

Repository / source / reference:

[`https://github.com/vishwaksen-1/words-kld-hash`](https://github.com/vishwaksen-1/words-kld-hash)

---

## What this post is about

This post compares:

- AES-128: ECB, CBC, CTR, CFB, OFB
- AES-256: ECB, CBC, CTR, CFB, OFB
- DES: ECB, CBC, CFB, OFB
- 3DES: ECB, CBC, CFB, OFB

The metrics are:

- byte entropy
- byte KL divergence to uniform
- n-gram KL
- repeated block ratio for 8-byte and 16-byte blocks

This post does not rank AES, DES, and 3DES as secure choices. DES is obsolete because its key is too small. Here it is included as a legacy comparison for output statistics and block-mode behavior.

---

## Background

Modern block ciphers are designed so ciphertext should not preserve simple plaintext statistics. If I encrypt English-looking bytes with AES-CBC or AES-CTR, the byte distribution should look close to uniform.

But block ciphers also need modes of operation. ECB mode encrypts identical plaintext blocks into identical ciphertext blocks under the same key. That means ECB can leak patterns even when the byte distribution looks random.

This is the important distinction:

```text
byte KL asks: do individual byte frequencies look uniform?
block repetition asks: do whole blocks repeat?
```

Those are different questions.

---

## Why this matters

ECB is a good example of why security analysis needs the right measurement. A byte histogram can look fine while a block-level view exposes a serious design problem.

This matters beyond ECB. In engineering work, a metric can be accurate and still incomplete. If the failure lives at the block level, a byte-level test is looking in the wrong place.

---

## Constraints

- Cost: local-only experiment.
- Time: run all cipher/mode combinations quickly.
- Hardware: ordinary laptop-scale compute.
- Compute: encryption, byte metrics, n-gram counts, block repetition counts.
- Tools: Python and `cryptography` primitives wrapped in `kldcrypto/modern.py`.
- Skills/context: educational measurement, not production cryptographic validation.
- Safety: clearly separate statistical output behavior from cryptographic recommendations.

The biggest constraint was constructing an input that actually demonstrates ECB leakage. The normal wordlist does not contain enough repeated 16-byte blocks to make the failure dramatic, so I added a synthetic repeated-block demo.

---

## System / Approach / Design

The modern cipher study encrypts the wordlist bytes with AES, DES, and 3DES across several modes.

Important decisions:

- Decision 1: include ECB alongside safer-looking modes.
    - Why: ECB is the cleanest example of random-looking bytes with leaked structure.
    - Alternative: omit ECB as obsolete.
    - Tradeoff: including it requires a strong warning, but it makes the metric failure visible.

- Decision 2: add a synthetic repeated-block input.
    - Why: the normal wordlist does not stress ECB enough.
    - Alternative: rely only on the wordlist.
    - Tradeoff: the synthetic input is artificial, but it isolates the failure.

- Decision 3: measure both 8-byte and 16-byte blocks.
    - Why: DES has an 8-byte block size and AES has a 16-byte block size.
    - Alternative: use only 16-byte blocks.
    - Tradeoff: two block sizes make the table wider, but the comparison is clearer.

---

## Implementation / What I did

The modern cipher outputs are generated like this:

```python
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
        rows.append(("DES", mode_name, des_encrypt(plaintext, mode_name)))

    for mode_name in ["ECB", "CBC", "CFB", "OFB"]:
        rows.append(("3DES", mode_name, triple_des_encrypt(plaintext, mode_name)))

    return rows
```

The ECB leakage demo uses repeated plaintext blocks:

```python
pattern_plaintext = (
    b"YELLOW SUBMARINE" * 1024
    + b"REPEATED-BLOCK!!" * 1024
)
```

The relevant outputs are:

- [`results/modern_cipher_modes.csv`](https://github.com/vishwaksen-1/words-kld-hash/blob/master/results/modern_cipher_modes.csv)
- [`results/modern_ngram_study.csv`](https://github.com/vishwaksen-1/words-kld-hash/blob/master/results/modern_ngram_study.csv)
- [`results/block_repetition_study.csv`](https://github.com/vishwaksen-1/words-kld-hash/blob/master/results/block_repetition_study.csv)
- [`results/ecb_repeated_block_demo.csv`](https://github.com/vishwaksen-1/words-kld-hash/blob/master/results/ecb_repeated_block_demo.csv)

---

## Tests / Observations

First, the byte-level metrics look good across modern cipher outputs:

| Method | Mode | Entropy bits/byte | KL(method \|\| uniform) |
| --- | --- | ---: | ---: |
| AES-128 | ECB | 7.9965 | 0.0024 |
| AES-128 | CBC | 7.9961 | 0.0027 |
| AES-128 | CTR | 7.9966 | 0.0023 |
| DES | ECB | 7.9963 | 0.0026 |
| DES | CBC | 7.9961 | 0.0027 |
| 3DES | ECB | 7.9970 | 0.0021 |
| 3DES | CBC | 7.9968 | 0.0022 |

At this level, ECB does not look alarming. AES-128 ECB has `KL(method || uniform) = 0.0024`, which is close to the other modes.

The block repetition demo tells the missing part of the story:

| Method | Mode | Block size | Repeated block ratio |
| --- | --- | ---: | ---: |
| Pattern Plain | repeated blocks | 16 | 99.90% |
| AES-128 | ECB | 16 | 99.85% |
| AES-128 | CBC | 16 | 0.00% |
| AES-128 | CTR | 16 | 0.00% |
| DES | ECB | 16 | 99.90% |
| DES | CBC | 16 | 0.00% |
| 3DES | ECB | 16 | 99.90% |
| 3DES | CBC | 16 | 0.00% |

ECB preserves equality between repeated plaintext blocks. CBC and CTR do not show repeated blocks in this synthetic test.

---

## What failed / What was surprising

What broke:

- Byte KL made ECB look normal.

Why it happened:

- ECB can produce byte distributions that look close to uniform while still mapping identical plaintext blocks to identical ciphertext blocks.

How I diagnosed it:

- I added block repetition analysis and then created a synthetic repeated-block plaintext.

What changed:

- The experiment suite gained a block-level metric instead of relying only on byte and n-gram distributions.

What tradeoff I accepted:

- The synthetic repeated-block input is not natural text, but it cleanly isolates the mode-of-operation failure.

---

## Result

- What works: byte KL confirms that modern cipher outputs look random-like at the byte level.
- What partially works: n-gram KL adds another lens, but it is still not the clearest detector for ECB.
- What does not work yet: byte KL alone cannot detect repeated-block leakage.
- What is untested: authentication, nonce misuse, padding oracle behavior, and real protocol-level failures.

The main result is that AES-ECB and AES-CBC can look similarly uniform by byte KL, while block repetition analysis separates them immediately on repeated-block input.

---

## What I learned

I expected ECB to fail the block repetition test. The useful part was seeing how normal it looked under the earlier byte-level metric.

That is the through-line of the whole series. Plaintext, classical ciphers, hashes, n-grams, and block modes each need measurements that match the structure being studied.

We obviously see that modern cipher bytes look close to uniform. But the main lesson is that random-looking bytes can still carry higher-level structure.

---

## Future work

- Next experiment: add authenticated encryption modes and nonce-misuse cases.
- Better measurement: visualize repeated blocks directly as an image grid.
- Cleaner implementation: split synthetic demos from natural wordlist experiments.
- Documentation needed: explain why DES appears statistically fine while being cryptographically obsolete.
- Open question: which small set of metrics gives the best beginner-friendly picture of structural leakage?
