import hashlib

def hash_file(path):
    with open(path, 'rb') as f:
        file_bytes = f.read()
        return hashlib.sha256(file_bytes).hexdigest()
