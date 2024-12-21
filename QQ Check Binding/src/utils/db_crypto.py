from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import base64

class DatabaseCrypto:
    def __init__(self, key_salt=None):
        self._salt = key_salt or get_random_bytes(32)
        self._key = PBKDF2(
            b'CHANGE_THIS_KEY', 
            self._salt,
            dkLen=32,
            count=1000000
        )
        
    def encrypt_query(self, query: str) -> str:
        """加密SQL查询"""
        iv = get_random_bytes(16)
        cipher = AES.new(self._key, AES.MODE_GCM, nonce=iv)
        ciphertext, tag = cipher.encrypt_and_digest(query.encode())
        return base64.b64encode(iv + tag + ciphertext).decode()
        
    def decrypt_result(self, encrypted_data: str) -> dict:
        """解密查询结果"""
        try:
            data = base64.b64decode(encrypted_data)
            iv = data[:16]
            tag = data[16:32]
            ciphertext = data[32:]
            cipher = AES.new(self._key, AES.MODE_GCM, nonce=iv)
            decrypted = cipher.decrypt_and_verify(ciphertext, tag)
            return eval(decrypted.decode())
        except:
            return None 