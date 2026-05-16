# Redis/redisvl-install

# RedisVL Installation

## Summary
RedisVL is a package designed for use with Redis that enhances its capabilities, particularly in the realm of AI. This document outlines the steps necessary to install RedisVL and set up a compatible Redis instance.

## Key Concepts
- **RedisVL**: A Python package that extends Redis functionalities, particularly for AI applications.
- **Redis Query Engine**: A feature of Redis that allows for advanced querying capabilities, which must be enabled for RedisVL to function properly.
- **Docker**: A platform used to run applications in containers, allowing for easy deployment and management of software environments.

## API Examples
To install the RedisVL package, use the following command in your Python environment (Python version 3.8 or higher):
```bash
pip install redisvl
```

To run a Redis instance with Redis Stack using Docker, execute:
```bash
docker run -d --name redis -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```
After running the above command, you can access the Redis Insight GUI at:
[http://localhost:8001](http://localhost:8001)

## Related Pages
- [Redis Documentation](https://redis.io/docs/)
- [Redis Stack Overview](https://redis.io/docs/stack/)
- [Docker Documentation](https://docs.docker.com/)

## Open Questions
- What are the specific AI functionalities provided by RedisVL?
- How does RedisVL compare to other AI frameworks in terms of performance and ease of use?
- Are there any limitations or prerequisites for using RedisVL with different versions of Redis?