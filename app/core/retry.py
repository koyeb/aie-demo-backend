import asyncio
import functools

from loguru import logger


class TooManyAttempts(Exception):
    pass


def with_retry(howmany: int, backoff: float):
    def wrapper(f):
        @functools.wraps(f)
        async def wrapped(*args, **kwargs):
            for i in range(howmany):
                try:
                    return await f(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"call #{i+1} failed: {str(e)}")
                    await asyncio.sleep(backoff)
                    pass

            raise TooManyAttempts()

        return wrapped

    return wrapper


if __name__ == "__main__":

    class Fallible(object):
        def __init__(self, min_attempts: int):
            self.min_attempts = min_attempts
            self.attempt = 0

        async def do(self):
            if self.attempt < self.min_attempts:
                print(f"failure: {self.attempt}")
                self.attempt += 1
                raise RuntimeError("Failure is granted")

            print(f"success: {self.attempt}")

    f1 = Fallible(1)

    f3 = Fallible(3)

    @with_retry(3, 0.3)
    async def will_succeed():
        await f1.do()

    @with_retry(3, 0.3)
    async def will_fail():
        await f3.do()

    asyncio.run(will_succeed())

    asyncio.run(will_fail())
