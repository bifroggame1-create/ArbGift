from slowapi import Limiter
from slowapi.util import get_remote_address

# In production we avoid starlette Config; Limiter just uses env directly
limiter = Limiter(key_func=get_remote_address)
