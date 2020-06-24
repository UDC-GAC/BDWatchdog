import os
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_mongodb_POST_endpoint():
    default_mongodb_port = 8001
    default_mongodb_ip = "mongodb"
    default_profiling_database_name = "cpu"
    PROFILING_POST_ENDPOINT = "PROFILING_POST_ENDPOINT"
    profiling_post_endpoint = os.getenv(PROFILING_POST_ENDPOINT, default_profiling_database_name)

    MONGODB_IP = "MONGODB_IP"
    mongodb_ip = os.getenv(MONGODB_IP, default_mongodb_ip)

    MONGODB_PORT = "MONGODB_PORT"
    try:
        mongodb_port = str(int(os.getenv(MONGODB_PORT, default_mongodb_port)))
    except ValueError:
        eprint("Invalid port configuration, using default '" + str(default_mongodb_port) + "'")
        mongodb_port = str(default_mongodb_port)

    post_endpoint = 'http://' + mongodb_ip + ':' + mongodb_port + '/' + profiling_post_endpoint
    return post_endpoint


def get_mongodb_GET_endpoint():
    default_mongodb_port = 8002
    default_mongodb_ip = "mongodb"

    MONGODB_IP = "MONGODB_IP"
    mongodb_ip = os.getenv(MONGODB_IP, default_mongodb_ip)

    MONGODB_PORT = "MONGODB_PORT"
    try:
        mongodb_port = str(int(os.getenv(MONGODB_PORT, default_mongodb_port)))
    except ValueError:
        eprint("Invalid port configuration, using default '" + str(default_mongodb_port) + "'")
        mongodb_port = str(default_mongodb_port)

    get_endpoint = 'http://' + mongodb_ip + ':' + mongodb_port + '/stacks/'
    return get_endpoint
