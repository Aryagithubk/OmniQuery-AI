from passlib.context import CryptContext
ctx = CryptContext(schemes=['bcrypt'])
print(ctx.verify('password', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'))
