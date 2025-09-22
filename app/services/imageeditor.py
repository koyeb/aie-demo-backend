import requests
from core.config import IMAGE_EDITOR_URL, IMAGE_EDITOR_API_KEY
import fs
from loguru import logger


class ImageEditor(object):
    def __init__(self, addr: str, api_key: str):
        self.api_key = api_key
        self.base_url = addr

    def _run(self, url: str, prompt: str):
        logger.debug("Requesting image editing")
        resp = requests.post(
            self.base_url + "/predict",
            json={
                "prompt": prompt,
                "input_image_url": url,
                "width": 1920,
                "height": 1080,
            },
        )

        if not resp or resp.status_code != 200:
            resp.raise_for_status()

        return resp.json()

    async def run(self, url: str, prompt: str) -> str:
        result = self._run(url, prompt)
        if not result or len(result["images"]) == 0 or not result["images"][0]:
            raise RuntimeError("No result returned")

        return result["images"][0].rsplit(",")[1]


image_editor = ImageEditor(IMAGE_EDITOR_URL, IMAGE_EDITOR_API_KEY)

if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url")
    parser.add_argument("-k", "--api-key")
    parser.add_argument("image")
    parser.add_argument("prompt")

    args = parser.parse_args()

    d = ImageEditor(args.url, args.api_key)

    res = asyncio.run(d.run(args.image, args.prompt))

    fpath = asyncio.run(fs.storage.save(res))
