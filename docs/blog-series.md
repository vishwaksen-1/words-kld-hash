# Blog Series Plan

## Series Title

Seeing Structure Disappear: KL Divergence, Hashing, and Encryption

## Through-Line

This series uses KL divergence, entropy, n-grams, and block repetition to study
how visible statistical structure changes under increasingly strong
transformations.

The framing should stay modest:

- KL divergence is a statistical lens.
- It is not a cryptographic security proof.
- It can still teach a lot about distinguishability and structural leakage.

## Post 1: Text Structure vs Hash Output

Working title:

> Does Hashing Make Text Look Random?

Use:

- `results/cipher_ladder.csv`
- `results/hash_family.csv`
- `plots/cipher_ladder_byte_distributions.png`
- `plots/cipher_ladder_kl_to_uniform.png`
- `plots/hash_family_kl_to_uniform.png`

Main result:

- Plaintext has entropy `4.2691` bits/byte and `KL(Plain || Uniform) = 2.5860`.
- DJB2 is much closer to uniform than plaintext, but still visibly less uniform than cryptographic hashes:
  - `KL(DJB2 || Uniform) = 0.0616`
- MD5, SHA-1, SHA-256, and SHA-512 all look close to uniform at byte level:
  - `KL(MD5 || Uniform) = 0.0011`
  - `KL(SHA-1 || Uniform) = 0.0009`
  - `KL(SHA-256 || Uniform) = 0.0005`
  - `KL(SHA-512 || Uniform) = 0.0003`

Message:

Hashing destroys much of the visible byte-frequency structure of the input
wordlist. But KL does not distinguish cryptographic safety: MD5 and SHA-1 can
look statistically uniform here while still being cryptographically broken.

## Post 2: Classical Ciphers

Working title:

> Ancient Ciphers Hide Text, But Do They Destroy Structure?

Use:

- `results/cipher_ladder.csv`
- `results/vigenere_key_study.csv`
- `results/xor_key_study.csv`
- `results/columnar_key_study.csv`
- `plots/vigenere_keylength_kl.png`
- `plots/xor_keylength_kl.png`
- `plots/columnar_columns_kl.png`

Main result:

- Caesar, substitution, and columnar transposition preserve byte entropy.
- Vigenere and XOR can move closer to uniform as key length and key randomness increase.
- Random byte keys flatten distributions much more than human-word keys.

Message:

Weak ciphers may obscure readability while preserving a lot of statistical
structure.

## Post 3: When Byte Frequencies Fail

Working title:

> Why Unigram KL Is Not Enough

Use:

- `results/ngram_window_study.csv`
- `plots/ngram_kl_to_uniform.png`
- `plots/ngram_entropy.png`

Main result:

- Columnar transposition is invisible to unigram KL:
  - unigram `KL(Plain || Columnar) = 0.0000`
- It becomes visible at larger windows:
  - bigram `KL(Plain || Columnar) = 0.3749`
  - trigram `KL(Plain || Columnar) = 2.0194`
  - 4-gram `KL(Plain || Columnar) = 11.7035`

Message:

Some transformations preserve byte counts but disrupt local order. Sliding
windows expose structure that unigram distributions miss.

## Post 4: AES, DES, and Block Modes

Working title:

> AES, DES, ECB, CBC: When Random-Looking Bytes Still Leak Structure

Use:

- `results/modern_cipher_modes.csv`
- `results/modern_ngram_study.csv`
- `results/block_repetition_study.csv`
- `results/ecb_repeated_block_demo.csv`
- `plots/modern_modes_kl_to_uniform.png`
- `plots/modern_ngram_kl_to_uniform.png`
- `plots/ecb_repeated_block_demo.png`

Main result:

- AES and DES-family outputs all look close to uniform at byte level.
- ECB can still leak repeated block structure.
- In the synthetic repeated-block demo:
  - AES-128 ECB repeat ratio is about `99.85%`.
  - AES-128 CBC repeat ratio is `0%`.
  - AES-128 CTR repeat ratio is `0%`.
  - DES ECB repeat ratio is about `99.90%`.
  - DES CBC repeat ratio is `0%`.

Message:

Byte KL says modern cipher outputs look random-like. Block analysis shows why
mode of operation still matters.

## Possible Final Reflection

The series should end with a matrix:

| Method | Byte KL useful? | N-gram KL useful? | Block repetition useful? |
| --- | --- | --- | --- |
| Plaintext | Yes | Yes | Sometimes |
| Caesar | Yes | Yes | Limited |
| Substitution | Partly | Yes | Limited |
| Columnar | No for unigrams | Yes | Sometimes |
| Vigenere/XOR | Yes | Yes | Key-dependent |
| SHA-256 | Yes as baseline | Sample-limited | No obvious structure |
| AES/DES CBC/CTR | Yes as baseline | Sample-limited | Yes for non-repetition |
| AES/DES ECB | Byte KL insufficient | Sometimes | Very useful |




<blockquote class="twitter-tweet" data-media-max-width="560"><p lang="en" dir="ltr">KL divergence asymmetry <a href="https://t.co/bvOAyCIMHw">pic.twitter.com/bvOAyCIMHw</a></p>&mdash; Ari Seff (@ari_seff) <a href="https://x.com/ari_seff/status/1303741288911638530?ref_src=twsrc%5Etfw">September 9, 2020</a></blockquote> <script async src="https://platform.x.com/widgets.js" charset="utf-8"></script>