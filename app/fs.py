import base64
import os.path
from pathlib import Path
from uuid import uuid4

import aiofiles
from loguru import logger

from core.config import LOCAL_PATH


class LocalStorage(object):
    def __init__(self, directory: str):
        """
        The object expects an existing directory where to save the files.
        """
        self.directory = Path(directory)

    async def save(self, content: str) -> str:
        """
        The function expects a base64-encoded image to be saved to a local path.
        The name is a randomly generated UUIDv4.
        """
        rand_id = str(uuid4())
        fpath = os.path.join(self.directory, rand_id)
        logger.debug("Saving file", path=fpath)
        decoded = base64.b64decode(content)
        async with aiofiles.open(fpath, "wb") as f:
            await f.write(decoded)

        return fpath


storage = LocalStorage(LOCAL_PATH)
