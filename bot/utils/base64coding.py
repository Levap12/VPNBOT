import base64

def encode(user_id):
    user_id_bytes = str(user_id).encode('utf-8')
    base64_bytes = base64.urlsafe_b64encode(user_id_bytes)
    base64_str = base64_bytes.decode('utf-8')
    return base64_str

def decode(encoded_user_id):
    base64_bytes = encoded_user_id.encode('utf-8')
    user_id_bytes = base64.urlsafe_b64decode(base64_bytes)
    user_id = int(user_id_bytes.decode('utf-8'))
    return user_id