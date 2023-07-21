import hashlib
import uuid

# 같은 문자열이면 같은 uuid 가지고싶음
def generate_uuid(name):
    # 이름을 바이트 문자열로 인코딩하여 SHA-256 해시값을 구합니다.
    hashed_name = hashlib.sha256(name.encode()).digest()
    
    # SHA-256 해시값으로 UUID를 생성합니다.
    generated_uuid = uuid.UUID(bytes=hashed_name[:16], version=5)
    return generated_uuid