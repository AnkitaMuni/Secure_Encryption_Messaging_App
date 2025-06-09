import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os

SECRET_HMAC_KEY = b'SuperSecretHMACKey'

def encrypt_message(key, plaintext):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    hmac_obj = hmac.new(SECRET_HMAC_KEY, encrypted_data, hashlib.sha256)
    hmac_digest = hmac_obj.digest()

    return iv + hmac_digest + encrypted_data

def decrypt_message(key, encrypted_packet):
    iv = encrypted_packet[:16]
    received_hmac = encrypted_packet[16:48]
    encrypted_text = encrypted_packet[48:]

    hmac_obj = hmac.new(SECRET_HMAC_KEY, encrypted_text, hashlib.sha256)
    expected_hmac = hmac_obj.digest()

    if not hmac.compare_digest(received_hmac, expected_hmac):
        raise ValueError("HMAC verification failed! Possible message tampering.")

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()

    decrypted_padded = decryptor.update(encrypted_text) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    decrypted_text = unpadder.update(decrypted_padded) + unpadder.finalize()

    return decrypted_text.decode()

