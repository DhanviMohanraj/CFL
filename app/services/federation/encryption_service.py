"""Encryption Service for Federated Updates.

Author: DriftAdapt Contributors
Purpose: Provides AES-256 GCM authenticated encryption to secure update payloads in transit.
"""

import os
import time
from typing import Tuple, Dict, Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.logging import LoggerFactory


class EncryptionService:
    """Service for securing federated payloads with AES-256-GCM authenticated encryption."""

    def __init__(self, symmetric_key: bytes) -> None:
        """Initializes the encryption service.
        
        Args:
            symmetric_key: A 32-byte (256-bit) cryptographic key for AES-256.
        """
        self._logger = LoggerFactory.get_logger("EncryptionService")
        if len(symmetric_key) != 32:
            raise ValueError(f"Symmetric key must be exactly 32 bytes for AES-256. Got {len(symmetric_key)} bytes.")
        
        self._key = symmetric_key
        self._aesgcm = AESGCM(self._key)

    def encrypt(self, data: bytes) -> Tuple[bytes, Dict[str, Any]]:
        """Encrypts data using AES-256-GCM.
        
        Args:
            data: The raw plaintext bytes to encrypt.
            
        Returns:
            Tuple containing:
            - The encrypted payload (nonce prepended to ciphertext).
            - A dictionary of statistics (duration).
        """
        start_time = time.perf_counter()
        
        # AES-GCM requires a unique nonce for every encryption operation with the same key
        # 12 bytes (96 bits) is the standard nonce length for AES-GCM
        nonce = os.urandom(12)
        
        # Encrypt the data. The authentication tag is automatically appended to the ciphertext.
        ciphertext = self._aesgcm.encrypt(nonce, data, associated_data=None)
        
        # Prepend the nonce so the decryptor can use it
        encrypted_payload = nonce + ciphertext
        
        duration = time.perf_counter() - start_time
        
        stats = {
            "algorithm": "aes-256-gcm",
            "duration_s": duration
        }
        
        self._logger.debug(f"Encrypted {len(data)} bytes in {duration:.3f}s.")
        return encrypted_payload, stats

    def decrypt(self, encrypted_payload: bytes) -> bytes:
        """Decrypts data using AES-256-GCM.
        
        Args:
            encrypted_payload: The encrypted bytes (nonce + ciphertext).
            
        Returns:
            The decrypted plaintext bytes.
            
        Raises:
            ValueError: If the payload is tampered with or corrupted.
        """
        if len(encrypted_payload) < 12:
            raise ValueError("Encrypted payload is too short to contain a nonce.")
            
        nonce = encrypted_payload[:12]
        ciphertext = encrypted_payload[12:]
        
        try:
            plaintext = self._aesgcm.decrypt(nonce, ciphertext, associated_data=None)
            return plaintext
        except Exception as e:
            self._logger.error("Decryption failed. Payload may be corrupted or tampered with.", error=str(e))
            raise ValueError("Decryption failed due to authentication tag mismatch or corruption.") from e

    @staticmethod
    def generate_key() -> bytes:
        """Generates a secure 32-byte key for AES-256."""
        return AESGCM.generate_key(bit_length=256)
