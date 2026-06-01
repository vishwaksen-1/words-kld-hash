---
title: Why Unigram KL Is Not Enough
tags: cryptography, n-grams, statistics, kl-divergence
---

# Why Unigram KL Is Not Enough

This is Part 3 of the series on KL divergence, hashing, and encryption outputs. The first two posts used byte frequencies as the main lens. That worked for plaintext, hashes, and some weak ciphers, but it missed an important kind of structure: order.

This post adds sliding-window n-grams. The main result is that columnar transposition is invisible to unigram KL, but visible once the metric starts looking at adjacent bytes.

Repository / source / reference:

[`https://github.com/vishwaksen-1/words-kld-hash`](https://github.com/vishwaksen-1/words-kld-hash)

---

## What this post is about

This post studies how the same transformations behave under different window sizes:

- 1-byte windows
- 2-byte windows
- 3-byte windows
- 4-byte windows
- 8-byte windows

The focus is not modern cryptographic security yet. The focus is a measurement failure: byte counts can stay the same while byte order changes.

---

## Background

A unigram model counts one byte at a time. If the letter `a` appears 100 times before a transformation and 100 times after it, the unigram count for `a` is unchanged.

That is useful, but limited. Text is not just a bag of characters. Local order matters. English has common pairs, triples, suffixes, prefixes, and repeated structures.

An n-gram model counts windows instead:

```text
unigram:  a
bigram:   ab
trigram:  abc
4-gram:   abcd
```

If a transformation preserves byte counts but disrupts adjacency, larger windows should notice.

---

## Why this matters

Metrics fail when they look at the wrong shape of evidence.

Columnar transposition is the example that made this obvious. It reorders bytes without changing which bytes exist. A unigram metric says nothing changed. But the human-readable message is clearly damaged, and the local byte relationships have changed.

N-grams are useful because they let the measurement ask a better question: did the transformation preserve local order?

---

## Constraints

The biggest constraint was sample size. The larger the window, the larger the possible n-gram space. For 8-byte windows, the theoretical support is `256^8`, which is enormous compared with this dataset.

---

## System / Approach / Design

The experiment reuses the transformation ladder from Part 2:

- Plain
- Identity
- Caesar
- Vigenere
- Columnar
- Substitution
- XOR
- SHA-256

For each window size, the script counts n-grams and computes:

- number of windows
- number of unique n-grams
- n-gram entropy
- KL divergence to uniform
- KL divergence between plaintext and method

Important decisions:

- Decision 1: use several fixed window sizes.
    - Why: the failure mode only appears when moving beyond unigrams.
    - Alternative: choose one larger window.
    - Tradeoff: multiple windows make the trend easier to see.

- Decision 2: keep 8-grams even though they are sample-limited.
    - Why: they show where interpretation becomes difficult.
    - Alternative: stop at 4-grams.
    - Tradeoff: the post needs a clear warning about sparse supports.

---

## Implementation / What I did

The n-gram study is generated in `h1-test2.py`:

```python
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
```

The relevant outputs are:

- [`results/ngram_window_study.csv`](https://github.com/vishwaksen-1/words-kld-hash/blob/master/results/ngram_window_study.csv)
- [`plots/ngram_kl_to_uniform.png`](https://github.com/vishwaksen-1/words-kld-hash/blob/master/plots/ngram_kl_to_uniform.png)
- [`plots/ngram_entropy.png`](https://github.com/vishwaksen-1/words-kld-hash/blob/master/plots/ngram_entropy.png)

---

## Tests / Observations

The key observation is columnar transposition across window sizes:

| Window | Unique columnar n-grams | KL(Plain \|\| Columnar) |
| ---: | ---: | ---: |
| 1 | 27 | 0.0000 |
| 2 | 652 | 0.3749 |
| 3 | 9154 | 2.0194 |
| 4 | 35581 | 11.7035 |
| 8 | 54322 | 16.7332 |

At window size `1`, columnar transposition is identical to plaintext under this metric. That is expected: it only reorders bytes.

At window size `2`, the metric starts to notice changed adjacency. By 3-grams and 4-grams, the difference is much larger.

The 8-gram result is useful, but more fragile. There are `54361` 8-byte windows and `54322` unique columnar 8-grams, so almost every observed window is unique. At that point, sample size becomes a major part of the story.

---

## What failed / What was surprising

What broke:

- Unigram KL completely missed columnar transposition.

Why it happened:

- The transformation preserved every byte count exactly.

How I diagnosed it:

- The unigram row had `KL(Plain || Columnar) = 0.0000`, while the bigram, trigram, and 4-gram rows increased sharply.

What changed:

- I added sliding-window measurements to the experiment suite.

What tradeoff I accepted:

- N-gram metrics are more sensitive to order, but larger windows become harder to interpret because the sample is sparse.

---

## Result

- What works: n-gram KL detects order disruption that unigram KL misses.
- What partially works: 8-gram analysis shows extreme sparsity, which is informative but not clean.
- What does not work yet: n-gram KL alone still does not explain block-mode failures like ECB.
- What is untested: natural-language token models, compression-based measures, and longer corpora.

The main result is that no single statistical view is enough. The metric has to match the kind of structure being investigated.

---

## What I learned

I expected larger windows to reveal more structure. I did not expect columnar transposition to become such a clean demonstration of the failure.

The unigram result is not wrong. It is answering a smaller question: did the byte counts change? For columnar transposition, the honest answer is no.

We obviously see that larger n-grams catch more order information. But the main lesson is that a correct metric can still be the wrong metric for the question.

---

## Future work

- Next experiment: compare modern cipher modes, especially ECB and CBC.
- Better measurement: add block repetition ratios for fixed block sizes.
- Cleaner implementation: separate n-gram plots by transformation family.
- Documentation needed: explain sample-size limits for sparse n-gram spaces.
- Open question: when should a project switch from n-grams to block-level structure tests?
