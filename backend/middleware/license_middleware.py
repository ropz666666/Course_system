from fastapi import FastAPI
from datetime import datetime, timezone
import base64
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from pathlib import Path

from common.exception import errors
from core.conf import settings

app = FastAPI()

# 加载公钥 (从文件)
with open(settings.SAPPER_PUBLIC_KEY, 'rb') as f:
    PUBLIC_KEY = serialization.load_pem_public_key(f.read())


# 加载许可证代码 (从txt文件)
def load_license_code():
    license_file = Path(settings.SAPPER_LICENSE_CODE)
    if not license_file.exists():
        raise FileNotFoundError(f"License file not found at {license_file}")

    with open(license_file, 'r', encoding='utf-8') as f:
        license_content = f.read().strip()

    if not license_content:
        raise ValueError("License file is empty")

    return license_content


LICENSE_CODE = load_license_code()


async def verify_license():
    try:
        # 检查许可证格式 (应该包含一个点分隔payload和signature)
        if LICENSE_CODE.count('.') != 1:
            raise errors.AuthorizationError(msg="无效的许可证格式，应为'payload.signature'")

        encoded_payload, encoded_signature = LICENSE_CODE.split('.')
        # 解码payload (添加必要的填充)
        payload = json.loads(base64.urlsafe_b64decode(encoded_payload).decode('utf-8'))

        # 验证有效期
        if 'expiry_time' not in payload:
            raise errors.AuthorizationError(msg="许可证缺少过期时间")

        expiry_time = datetime.fromisoformat(payload['expiry_time']).astimezone(timezone.utc)
        current_time = datetime.now(timezone.utc)

        if current_time > expiry_time:
            expiry_str = expiry_time.strftime('%Y-%m-%d %H:%M:%S UTC')
            current_str = current_time.strftime('%Y-%m-%d %H:%M:%S UTC')
            raise errors.AuthorizationError(
                msg=f"证书已过期 (当前时间: {current_str}, 过期时间: {expiry_str})"
            )

        # 验证签名
        signature = base64.urlsafe_b64decode(encoded_signature)
        PUBLIC_KEY.verify(
            signature,
            json.dumps(payload).encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return True

    except (ValueError, json.JSONDecodeError) as e:
        raise errors.AuthorizationError(msg="许可证解析失败") from e
    except Exception as e:
        raise errors.AuthorizationError(msg="许可证验证失败") from e