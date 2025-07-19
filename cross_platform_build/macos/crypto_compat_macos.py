"""
加密兼容性模块 - macOS版本
解决 PyInstaller 打包时 hashlib.pbkdf2_hmac 缺失的问题
"""

import hashlib
import hmac
import os
from werkzeug.security import generate_password_hash as _original_generate_password_hash
from werkzeug.security import check_password_hash


def pbkdf2_hmac_fallback(hash_name, password, salt, iterations, dklen=None):
    """
    pbkdf2_hmac 的后备实现
    当系统的 hashlib.pbkdf2_hmac 不可用时使用
    """
    if isinstance(password, str):
        password = password.encode('utf-8')
    if isinstance(salt, str):
        salt = salt.encode('utf-8')
    
    # 使用 HMAC 实现 PBKDF2
    hash_func = getattr(hashlib, hash_name)
    if dklen is None:
        dklen = hash_func().digest_size
    
    def prf(data):
        return hmac.new(password, data, hash_func).digest()
    
    # PBKDF2 实现
    result = b''
    i = 1
    while len(result) < dklen:
        u = prf(salt + i.to_bytes(4, 'big'))
        f = u
        for _ in range(iterations - 1):
            u = prf(u)
            f = bytes(a ^ b for a, b in zip(f, u))
        result += f
        i += 1
    
    return result[:dklen]


def safe_generate_password_hash(password, method='pbkdf2:sha256', salt_length=8):
    """
    安全的密码哈希生成函数
    在 PyInstaller 环境中提供后备方案
    """
    try:
        # 首先尝试使用原始的 werkzeug 函数
        return _original_generate_password_hash(password, method=method, salt_length=salt_length)
    except AttributeError as e:
        if 'pbkdf2_hmac' in str(e):
            # 如果 pbkdf2_hmac 不可用，使用后备方案
            print(f"警告: hashlib.pbkdf2_hmac 不可用，使用后备实现")
            
            # 生成随机盐
            salt = os.urandom(salt_length)
            
            # 解析方法参数
            if method.startswith('pbkdf2:'):
                hash_name = method.split(':', 1)[1]
                iterations = 260000  # werkzeug 默认迭代次数
            else:
                hash_name = 'sha256'
                iterations = 260000
            
            # 使用后备实现
            key = pbkdf2_hmac_fallback(hash_name, password, salt, iterations)
            
            # 格式化为 werkzeug 兼容的格式
            import base64
            salt_b64 = base64.b64encode(salt).decode('ascii')
            key_b64 = base64.b64encode(key).decode('ascii')
            
            return f"pbkdf2:{hash_name}:{iterations}${salt_b64}${key_b64}"
        else:
            raise


# 猴子补丁：替换 hashlib.pbkdf2_hmac（如果不存在）
if not hasattr(hashlib, 'pbkdf2_hmac'):
    print("警告: 系统缺少 hashlib.pbkdf2_hmac，应用后备实现")
    hashlib.pbkdf2_hmac = pbkdf2_hmac_fallback


# 导出函数
__all__ = ['safe_generate_password_hash', 'check_password_hash', 'pbkdf2_hmac_fallback']
