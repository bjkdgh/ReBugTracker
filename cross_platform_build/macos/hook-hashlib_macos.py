# PyInstaller hook for hashlib module - macOS版本
# 确保 hashlib.pbkdf2_hmac 函数被正确包含

from PyInstaller.utils.hooks import collect_all

# 收集所有 hashlib 相关的模块
datas, binaries, hiddenimports = collect_all('hashlib')

# 添加额外的隐藏导入
hiddenimports += [
    '_hashlib',
    '_sha1',
    '_sha256', 
    '_sha512',
    '_md5',
    'binascii',
    'hmac',
]

# 确保包含 pbkdf2_hmac 相关的底层模块
try:
    import _hashlib
    hiddenimports.append('_hashlib')
except ImportError:
    pass

try:
    import hashlib
    # 测试 pbkdf2_hmac 是否可用
    if hasattr(hashlib, 'pbkdf2_hmac'):
        hiddenimports.append('hashlib')
except ImportError:
    pass
