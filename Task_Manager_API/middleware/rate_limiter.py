import time
from functools import wraps
from flask import request

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


ip_queue = defaultdict(deque)

GLOBAL_LIMIT = 2000


def global_limit(current_counter: int):
    # layer 1 [total request , and all stuff, sliding window rate limiter ]
    # 2000/hour TTL
    if current_counter >= GLOBAL_LIMIT:
        return too_many_requests(
            msg="Service  Got more request than it required in mean time"
        )


def per_ip(ip, current_count, limit):
    # layer 2 [check the per ip request if it is increase than required this brother is banned for 20-30 minutes]
    # sliding window rate limiter
    # 5 request/min TTL
    if current_count > limit:
        return too_many_requests(msg="Same Ip done more request than required")


def per_user():
    # layer 3 [check the failure of the login or signups ]
    # only failure based 5 failed login will ban the user for 15 minute from accessing that particular user and all
    # to check if he had any f
    pass


##############################################################################################
# Trying to use the double ended queue data strucure to sliding window technique without redis
# ############################################################################################


def sliding_window(window_queue, window_size, limit, arrival_time=None):
    # i think  first  check should be the  that the currently the incoming  request can be entertained or Not
    # why add to the deque if it is  not  valid just dont allow

    if arrival_time is None:
        arrival_time = time.time()

    while window_queue and window_queue[0] <= (arrival_time - window_size):
        window_queue.popleft()

    if len(window_queue) >= limit:
        return False

    window_queue.append(arrival_time)
    return True


def rate_limit(key_prefix, limit, window_size):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            window_queue = ip_queue[ip]

            if sliding_window(window_queue, window_size, limit):
                return f(*args, **kwargs)

            else:
                return too_many_requests(msg="Rate Limit Exceeded ::) ")

        return wrapper

    return decorator
