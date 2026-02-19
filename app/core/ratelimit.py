import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.config import Config as StarletteConfig

# Avoid starlette Config trying to read missing .env in container
_config = StarletteConfig(env_file=None, environ=os.environ)
limiter = Limiter(key_func=get_remote_address, config=_config)
