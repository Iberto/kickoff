from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
# TODO: enhancement
# make the limit less predictable by using a sliding window instead of a fixed one
# limiter = Limiter(key_func=get_remote_address, strategy="moving-window")
