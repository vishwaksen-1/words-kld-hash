# KL Divergence Experiments on Hashing and Encryption Outputs

This project is an empirical, educational framework for studying how statistical
structure changes under hashing and encryption.

The core question is not "does KL divergence prove cryptographic security?"
It does not. The useful question is:

> How much statistical structure is visible under different transformations, and
> where do byte-level KL measurements fail?

### Wordlist
Using this wordlist - [`SecLists/Miscellaneous/Words/EFF-Dice/large_words.txt`](https://github.com/danielmiessler/SecLists/blob/master/Miscellaneous/Words/EFF-Dice/large_words.txt) - as [wordlist.txt](wordlist.txt) in this project.

Found at [SecLists](https://github.com/danielmiessler/SecLists).

This is [EFF Diceware](https://www.eff.org/dice) wordlist, which contains 7776 unique English words. 

## Run

### Setup virtual environment 

```
python -m venv .venv
source .venv/bin/activate
```

### Install dependencies
```
pip install -r requirements.txt
```

### Run experiments
```
python h1-test1-plainVShash.py
python test2.py
```

The script writes:

- CSV tables to `results/`
- plots to `plots/`

To print the key blog tables from the latest CSV files:

```bash
python blog_summary.py
```

## Current Experiment Set

- Plaintext vs SHA-256
- Hash family comparison:
  - DJB2
  - CRC-24
  - MD5
  - SHA-1
  - SHA-256
  - SHA-512
- Classical ciphers:
  - identity
  - Caesar
  - Vigenere
  - columnar transposition
  - substitution
  - repeating-key XOR
- Key-length/randomness studies for Vigenere and XOR
- Sliding-window n-gram analysis
- Modern cipher modes:
  - AES-128 / AES-256: ECB, CBC, CTR, CFB, OFB
  - DES: ECB, CBC, CFB, OFB
  - 3DES: ECB, CBC, CFB, OFB
- Block repetition analysis for ECB leakage

## Important Framing

KL divergence and entropy are statistical tools, not security proofs.

They can show that plaintext is structured, hashes/ciphers often look close to
uniform at byte level, and weak transformations preserve detectable structure.
But some failures, especially ECB mode, require block-level analysis rather than
byte-frequency KL alone.
