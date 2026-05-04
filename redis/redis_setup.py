import redis

def init_redis_data():
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    client = redis.Redis(connection_pool=pool)

    # Initialize String
    client.set('sample_string', 'Hello World')

    # Initialize List
    client.lpush('sample_list', 'item1', 'item2', 'item3')

    # Initialize Hash
    client.hset('sample_hash', mapping={'field1': 'value1', 'field2': 'value2'})

    # Initialize Stream
    client.xadd('sample_stream', {'field1': 'value1', 'field2': 'value2'})

    # Initialize Sorted Set
    client.zadd('sample_zset', {'member1': 1, 'member2': 2, 'member3': 3})

if __name__ == '__main__':
    init_redis_data()