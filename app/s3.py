import base64
from io import BytesIO
import typing as T
from uuid import uuid4

from gcloud.aio.storage import Storage, Blob
from loguru import logger

from core.config import S3_BUCKET


class S3Storage(object):
    def __init__(self, bucket: str):
        """
        The object manages uploads to a bucket and also the creation
        of temporary download urls.
        """
        self.bucket = bucket

    @staticmethod
    def _get_id(obj_url: str) -> str:
        if obj_url.startswith("gs://"):
            url = obj_url.lstrip("gs://")
            parts = url.split("/")
            if len(parts) < 2:
                raise RuntimeError(f"Invalid gcs url: {obj_url}")
            return "/".join(parts[1:])

        return obj_url

    async def save(self, content: str) -> str:
        """
        The function expects a base64-encoded image to be saved to a remote
        s3 bucket. The resource name is randomly generated.
        """
        rand_id = str(uuid4())
        decoded = base64.b64decode(content)

        async with Storage() as client:
            try:
                logger.debug("uploading to s3", bucket=self.bucket, obj_id=rand_id)
                await client.upload(self.bucket, rand_id, BytesIO(decoded))
            except Exception:
                logger.exception("failed to upload file")
                raise

        logger.info("uploaded to s3", bucket=self.bucket, obj_id=rand_id)
        return f"gs://{self.bucket}/{rand_id}"

    async def get_presigned_url(self, obj_url: str, expiration: int = 300) -> str:
        """
        Given the id of the file, generate a presigned URL to share it with some other service.
        """
        obj_id = self._get_id(obj_url)

        async with Storage() as client:
            bucket = client.get_bucket(self.bucket)
            blob = await bucket.get_blob(obj_id)
            res = await self._get_presigned_url(blob, expiration)

        return res

    async def _get_presigned_url(self, blob: Blob, expiration: int) -> str:
        try:
            logger.debug(
                "generating presigned url", bucket=self.bucket, obj_id=blob.name
            )
            resp = await blob.get_signed_url(expiration)
        except Exception:
            logger.exception("failed to generate presigned url")
            raise

        logger.info(
            "presigned url generated", bucket=self.bucket, obj_id=blob.name, resp=resp
        )

        return resp


storage = S3Storage(S3_BUCKET)


if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--fpath")
    parser.add_argument("-b", "--bucket")

    args = parser.parse_args()

    m = S3Storage(args.bucket)

    with open(args.fpath, "rb") as f:
        image_bin = f.read()
        content = base64.b64encode(image_bin)

    url = asyncio.run(m.save(content))
    print(url)

    obj_id = m._get_id(url)
    print(obj_id)

    dl_url = asyncio.run(m.get_presigned_url(url))
    print(dl_url)
