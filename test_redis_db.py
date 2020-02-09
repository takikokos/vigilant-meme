import redis


redisClient = redis.Redis(host='localhost', port=6379, db=0)
print("Be sure redis-server is working")
print("Extracting all audios from db....")
for id in redisClient.keys():
    length = redisClient.llen(id)
    for i in range(length):
        audio = redisClient.lpop(id)
        with open(f"{id.decode()}_{i}_audio", "wb") as out:
            out.write(audio)
        redisClient.rpush(id, audio)