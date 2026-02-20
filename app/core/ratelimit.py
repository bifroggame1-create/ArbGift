import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# Ensure empty .env exists so SlowAPI/Starlette Config does not fail
if not os.path.exists('.env'):
    open('.env', 'a').close()

limiter = Limiter(key_func=get_remote_address)
