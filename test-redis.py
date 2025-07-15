import redis

r = redis.Redis(
    host='redis-14060.c12.us-east-1-4.ec2.redns.redis-cloud.com',
    port=14060,
    decode_responses=True,
    username="default",
    password="DAlguXsQfmtgr9si8LhdD6cWeNRCyyc5",
)

r.set("foo", "bar")
print("✅ Redis value:", r.get("foo"))

