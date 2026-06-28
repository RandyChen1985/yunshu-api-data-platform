"""
API Key Encryption and Management
使用 Fernet 对称加密实现 API Key 的安全存储和检索
"""
import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
from typing import Tuple
from app.core.config import settings


class APIKeyManager:
    """API Key 加密管理器"""
    
    def __init__(self):
        """初始化加密管理器，从环境变量读取密钥"""
        encryption_key = settings.ENCRYPTION_KEY
        
        if not encryption_key:
            raise ValueError(
                "ENCRYPTION_KEY environment variable is not set. "
                "Please generate one using: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )
        
        try:
            # Fernet 需要 bytes 类型的密钥
            self.cipher = Fernet(encryption_key.encode())
        except Exception as e:
            raise ValueError(f"Invalid encryption key format: {e}")
    
    def generate_api_key(self) -> Tuple[str, str, str]:
        """
        生成新的 API Key（明文、加密、哈希）
        
        Returns:
            Tuple[str, str, str]: (plaintext_key, encrypted_key, hashed_key)
            - plaintext_key: 原始 API Key（返回给用户，仅此一次）
            - encrypted_key: 加密后的 API Key（存储到数据库 api_key_encrypted 字段）
            - hashed_key: SHA256 哈希值（存储到数据库 api_key_hash 字段，用于快速验证）
        """
        # 1. 生成 32 字节的随机 API Key
        api_key = secrets.token_urlsafe(32)
        
        # 2. 加密存储（可解密）
        encrypted = self.cipher.encrypt(api_key.encode())
        encrypted_b64 = base64.urlsafe_b64encode(encrypted).decode()
        
        # 3. 计算哈希值（用于快速验证）
        hashed = hashlib.sha256(api_key.encode()).hexdigest()
        
        return api_key, encrypted_b64, hashed
    
    def encrypt_api_key(self, plaintext_key: str) -> str:
        """
        加密 API Key
        
        Args:
            plaintext_key: 原始 API Key 明文
        
        Returns:
            str: Base64 编码的加密 API Key
        """
        encrypted = self.cipher.encrypt(plaintext_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """
        解密 API Key
        
        Args:
            encrypted_key: Base64 编码的加密 API Key
        
        Returns:
            str: 原始 API Key 明文
        
        Raises:
            ValueError: 解密失败（密钥错误或数据损坏）
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt API Key: {e}")
    
    def hash_api_key(self, api_key: str) -> str:
        """
        计算 API Key 的 SHA256 哈希值
        
        Args:
            api_key: 原始 API Key
        
        Returns:
            str: SHA256 哈希值（十六进制字符串）
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def verify_api_key(self, plaintext_key: str, hashed_key: str) -> bool:
        """
        验证 API Key 是否匹配
        
        Args:
            plaintext_key: 用户提供的 API Key
            hashed_key: 数据库中存储的哈希值
        
        Returns:
            bool: 是否匹配
        """
        computed_hash = self.hash_api_key(plaintext_key)
        return computed_hash == hashed_key


# 全局单例实例
_api_key_manager = None


def get_api_key_manager() -> APIKeyManager:
    """获取 APIKeyManager 单例实例"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager
