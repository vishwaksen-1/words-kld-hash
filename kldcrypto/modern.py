import hashlib
import subprocess

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.decrepit.ciphers import modes as decrepit_modes
from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def aes_encrypt(byte_data, mode_name, key_size=128, key_seed=b"aes-key", iv_seed=b"aes-iv"):
    key = derive_bytes(key_seed + str(key_size).encode("ascii"), key_size // 8)
    return _cryptography_encrypt(byte_data, algorithms.AES(key), mode_name, iv_seed)


def triple_des_encrypt(byte_data, mode_name, key_seed=b"triple-des-key", iv_seed=b"triple-des-iv"):
    key = derive_bytes(key_seed, 24)
    return _cryptography_encrypt(byte_data, TripleDES(key), mode_name, iv_seed)


def des_encrypt(byte_data, mode_name, key_seed=b"des-key", iv_seed=b"des-iv"):
    key = derive_bytes(key_seed, 8)
    block_size = 8
    mode_name = mode_name.upper()
    cipher_name = {
        "ECB": "des-ecb",
        "CBC": "des-cbc",
        "CFB": "des-cfb",
        "OFB": "des-ofb",
    }[mode_name]

    data = byte_data
    if mode_name in {"ECB", "CBC"}:
        data = pkcs7_pad(byte_data, block_size)

    cmd = [
        "openssl",
        "enc",
        "-provider",
        "legacy",
        "-provider",
        "default",
        f"-{cipher_name}",
        "-K",
        key.hex(),
        "-nosalt",
    ]
    if mode_name != "ECB":
        cmd.extend(["-iv", derive_bytes(iv_seed + mode_name.encode("ascii"), block_size).hex()])
    if mode_name in {"ECB", "CBC"}:
        cmd.append("-nopad")

    proc = subprocess.run(cmd, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", errors="replace").strip())

    return proc.stdout


def derive_bytes(seed, length):
    output = bytearray()
    counter = 0
    while len(output) < length:
        output.extend(hashlib.sha256(seed + counter.to_bytes(4, "big")).digest())
        counter += 1
    return bytes(output[:length])


def pkcs7_pad(byte_data, block_size):
    pad_len = block_size - (len(byte_data) % block_size)
    if pad_len == 0:
        pad_len = block_size
    return byte_data + bytes([pad_len]) * pad_len


def _cryptography_encrypt(byte_data, algorithm, mode_name, iv_seed):
    mode_name = mode_name.upper()
    block_size = algorithm.block_size // 8

    if mode_name == "ECB":
        mode = modes.ECB()
        data = pkcs7_pad(byte_data, block_size)
    elif mode_name == "CBC":
        mode = modes.CBC(derive_bytes(iv_seed + mode_name.encode("ascii"), block_size))
        data = pkcs7_pad(byte_data, block_size)
    elif mode_name == "CTR":
        mode = modes.CTR(derive_bytes(iv_seed + mode_name.encode("ascii"), block_size))
        data = byte_data
    elif mode_name == "CFB":
        mode = decrepit_modes.CFB(derive_bytes(iv_seed + mode_name.encode("ascii"), block_size))
        data = byte_data
    elif mode_name == "OFB":
        mode = decrepit_modes.OFB(derive_bytes(iv_seed + mode_name.encode("ascii"), block_size))
        data = byte_data
    else:
        raise ValueError(f"unsupported mode: {mode_name}")

    cipher = Cipher(algorithm, mode, backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(data) + encryptor.finalize()
