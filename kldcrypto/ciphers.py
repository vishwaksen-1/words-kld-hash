import hashlib
import random


def identity(byte_data):
    return bytes(byte_data)


def caesar_shift(byte_data, shift=3):
    return bytes((b + shift) % 256 for b in byte_data)


def vigenere_encrypt(byte_data, key):
    key = _require_key(key)
    return bytes((b + key[i % len(key)]) % 256 for i, b in enumerate(byte_data))


def xor_repeating_key(byte_data, key):
    key = _require_key(key)
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(byte_data))


def columnar_transposition(byte_data, columns):
    if columns < 2:
        raise ValueError("columns must be >= 2")

    rows = [byte_data[i:i + columns] for i in range(0, len(byte_data), columns)]
    output = bytearray()
    for col in range(columns):
        for row in rows:
            if col < len(row):
                output.append(row[col])

    return bytes(output)


def substitution_cipher(byte_data, key=b"default-substitution-key"):
    permutation = substitution_permutation(key)
    return bytes(permutation[b] for b in byte_data)


def substitution_permutation(key):
    seed = int.from_bytes(hashlib.sha256(_require_key(key)).digest(), "big")
    rng = random.Random(seed)
    values = list(range(256))
    rng.shuffle(values)
    return values


def sha256_each_word(words):
    return b"".join(hashlib.sha256(word.encode("utf-8")).digest() for word in words)


def hash_each_word(words, algorithm):
    algorithm = algorithm.lower()
    if algorithm == "djb2":
        return b"".join(djb2(word.encode("utf-8")).to_bytes(4, "big") for word in words)
    if algorithm == "crc24":
        return b"".join(crc24(word.encode("utf-8")).to_bytes(3, "big") for word in words)
    if algorithm in {"md5", "sha1", "sha256", "sha512"}:
        return b"".join(hashlib.new(algorithm, word.encode("utf-8")).digest() for word in words)
    raise ValueError(f"unsupported hash algorithm: {algorithm}")


def djb2(byte_data):
    value = 5381
    for b in byte_data:
        value = ((value << 5) + value + b) & 0xFFFFFFFF
    return value


def crc24(byte_data):
    # OpenPGP CRC-24: poly 0x1864CFB, init 0xB704CE.
    crc = 0xB704CE
    for b in byte_data:
        crc ^= b << 16
        for _ in range(8):
            crc <<= 1
            if crc & 0x1000000:
                crc ^= 0x1864CFB
            crc &= 0xFFFFFF
    return crc


def random_ascii_key(length, rng):
    alphabet = b"abcdefghijklmnopqrstuvwxyz"
    return bytes(rng.choice(alphabet) for _ in range(length))


def random_byte_key(length, rng):
    return bytes(rng.randrange(256) for _ in range(length))


def _require_key(key):
    if isinstance(key, str):
        key = key.encode("utf-8")
    if not key:
        raise ValueError("key must not be empty")
    return bytes(key)
