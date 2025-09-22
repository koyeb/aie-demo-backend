import asyncio
import functools


def with_lock(lock: asyncio.Lock):
    def wrapper(f):
        @functools.wraps(f)
        async def wrapped(*args):
            async with lock:
                return await f(*args)

        return wrapped

    return wrapper


if __name__ == "__main__":
    tmp_lock = asyncio.Lock()

    @with_lock(tmp_lock)
    async def probe(context: str):
        print(f"{context} ----> 1")
        await asyncio.sleep(1)
        print(f"{context} ----> 2")
        await asyncio.sleep(1)
        print(f"{context} ----> 3")
        await asyncio.sleep(1)

    async def _run():
        await asyncio.gather(
            probe("FIRST"),
            probe("SECOND"),
            probe("THIRD"),
        )

    asyncio.run(_run())
