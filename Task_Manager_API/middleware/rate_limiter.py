import time
from functools import wraps
from flask import request
from flask_task_manager import logging

# import redis
from flask_task_manager.utils import too_many_requests
from collections import defaultdict, deque

# redis_client = redis.Redis(
#     host=current_app.get("REDIS_HOST", "localhost"),
#     port=current_app.get("REDIS_PORT", 6379),
#     decode_responses=True,
# )

# for normal testing
# redis_client = redis.Redis(
#     host="localhost",
#     port=6379,
#     decode_responses=True,
# )
#

logger = logging.getLogger(__name__)
ip_queue = defaultdict(deque)


##############################################################################################
# Trying to use the double ended queue data strucure to sliding window technique without redis
# ############################################################################################


def sliding_window(window_queue, window_size, limit, key_ip, arrival_time=None):
    # i think  first  check should be the  that the currently the incoming  request can be entertained or Not
    # why add to the deque if it is  not  valid just dont allow

    if arrival_time is None:
        arrival_time = time.time()

    while window_queue and window_queue[0] <= (arrival_time - window_size):
        window_queue.popleft()

    logger.info(f"window_queue : {window_queue}")
    if not window_queue and key_ip in window_queue:
        del ip_queue[key_ip]

    if len(window_queue) >= limit:
        return False

    window_queue.append(arrival_time)
    return True


def sliding_window_per_user(window_queue, window_size, limit, arrival_time):
    # but how  we get the  username i thought , then this  came to my mind first decorator run would be the app.route one
    # then we can use the  request function to get the username and do a sruff
    while window_queue and window_queue[0] <= (arrival_time - window_size):
        window_queue.popleft()
    if len(window_queue) >= limit:
        return False

    return True


def rate_limit(key_prefix, limit, window_size):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.headers.get("X-Forwarded-For", request.remote_addr)
            key_ip = f"{key_prefix}:{ip}"
            window_queue = ip_queue[key_ip]

            if sliding_window(window_queue, window_size, limit, key_ip):
                return f(*args, **kwargs)

            else:
                return too_many_requests(msg="Rate Limit Exceeded ::) ")

        return wrapper

    return decorator
