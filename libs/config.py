import os
current_path = os.path.dirname(os.path.realpath(__file__))
CONFIG = {
    # at least 3 nodes as per problem statement
    'APPLICATION_SERVER_IP': 'localhost',
    'APPLICATION_SERVER_PORT': 6600,
    'SERVER_POOL': {
        'n1': ('127.0.0.1', 30008), 
        'n2': ('127.0.0.1', 30009), 
        'n3': ('127.0.0.1', 30010),
    },
    'HEALTH_THRESHOLD': 2,
    'BACKUP_CACHE_SECONDS': 10,
    'BACKUP_DIR': current_path + "/../backup",
    'BACKUP_FILENAME_FORMAT': current_path + "/../backup/_bc_",
    'MAX_CLIENTS': 100,
    'MAX_CONNECTIONS': 100,
    'LRU_CAPACITY': 100,
    'MAX_HEADER_SIZE': 128,
}