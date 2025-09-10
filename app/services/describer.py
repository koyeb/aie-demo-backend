import base64

import aiofiles
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from loguru import logger

from core.config import DESCRIBER_URL, DESCRIBER_API_KEY


SYSTEM_PROMPT = "You are a helpful assistant whose aim is to give the best possible description of any given image, with particular focus on identifying content and position of any text appearing in the image"
USER_PROMPT = (
    "Describe the provided image. What is written on the image and where is it located?"
)


class Describer(object):
    def __init__(self, addr: str, api_key: str):
        self.ai = AsyncOpenAI(
            base_url=addr,
            api_key=api_key,
        )

    async def run(self, fpath: str, ftype: str = "png") -> ChatCompletion:
        async with aiofiles.open(fpath, "rb") as f:
            data = await f.read()
            image_b64_content = base64.b64encode(data)

        logger.debug("image loaded", fpath=fpath)

        return await self.ai.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": SYSTEM_PROMPT,
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{ftype};base64,{image_b64_content.decode('ascii')}"
                            },
                        },
                        {
                            "type": "text",
                            "text": USER_PROMPT,
                        },
                    ],
                },
            ],
            model="Qwen/Qwen2.5-VL-72B-Instruct",
            max_tokens=100,
        )


describer = Describer(DESCRIBER_URL, DESCRIBER_API_KEY)

if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url")
    parser.add_argument("-k", "--api-key")
    parser.add_argument("-p", "--fpath")

    args = parser.parse_args()

    d = Describer(args.url, args.api_key)

    res = asyncio.run(d.run(args.fpath))

    print(res.to_json(indent=4))
