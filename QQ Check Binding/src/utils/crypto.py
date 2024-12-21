from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib
import os

class SecurityProvider:
    def __init__(self):
        # 使用环境变量或硬编码的密钥（生产环境建议使用环境变量）
        self._key = hashlib.sha256(b'YOUR_SECRET_KEY').digest()
        self._iv = os.urandom(16)  # 随机初始化向量
        
    def encrypt_data(self, data: str) -> str:
        """加密数据"""
        cipher = AES.new(self._key, AES.MODE_CBC, self._iv)
        encrypted = cipher.encrypt(pad(data.encode(), AES.block_size))
        return base64.b64encode(self._iv + encrypted).decode()
        
    def decrypt_data(self, encrypted_data: str) -> str:
        """解密数据"""
        raw = base64.b64decode(encrypted_data)
        iv = raw[:16]
        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(raw[16:]), AES.block_size)
        return decrypted.decode() 