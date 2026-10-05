import hashlib
import os

class SecurityUtils:
    @staticmethod
    def hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
        """
        Hashes a password using PBKDF2-HMAC-SHA256.
        Returns a tuple of (hex_hash, hex_salt).
        """
        if salt is None:
            salt = os.urandom(16)
            
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        return pwd_hash.hex(), salt.hex()

    @staticmethod
    def verify_password(stored_hash: str, stored_salt: str, provided_password: str) -> bool:
        """
        Verifies a provided password against the stored hash and salt.
        """
        salt_bytes = bytes.fromhex(stored_salt)
        new_hash, _ = SecurityUtils.hash_password(provided_password, salt_bytes)
        return new_hash == stored_hash
