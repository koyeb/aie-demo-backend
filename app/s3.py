import base64
from io import BytesIO
from uuid import uuid4

import aioboto3
from botocore.client import Config
from botocore.handlers import set_list_objects_encoding_type_url
from loguru import logger


class S3Storage(object):
    def __init__(self, bucket: str, access_key: str, access_secret: str):
        """
        The object manages uploads to a bucket and also the creation
        of temporary download urls.
        """
        self.bucket = bucket
        self.access_key = access_key
        self.access_secret = access_secret

    def get_session(self) -> aioboto3.Session:
        session = aioboto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.access_secret,
            region_name="EUROPE-WEST9",
        )
        session.events.unregister(
            "before-parameter-build.s3.ListObjects", set_list_objects_encoding_type_url
        )
        return session

    async def save(self, content: str) -> str:
        """
        The function expects a base64-encoded image to be saved to a remote
        s3 bucket. The resource name is randomly generated.
        """
        rand_id = str(uuid4())
        decoded = base64.b64decode(content)
        session = self.get_session()
        async with session.client(
            "s3",
            endpoint_url="https://storage.googleapis.com",
            config=Config(signature_version="s3v4"),
        ) as s3:
            try:
                logger.debug("uploading to s3", bucket=self.bucket, obj_id=rand_id)
                await s3.upload_fileobj(BytesIO(decoded), self.bucket, rand_id)
            except Exception:
                logger.exception("failed to upload file")
                raise

        logger.info("uploaded to s3", bucket=self.bucket, obj_id=rand_id)
        return f"s3://{self.bucket}/{rand_id}"

    async def get_presigned_url(self, obj_id: str) -> str:
        """
        Given the id of the file, generate a presigned URL to share it with some other service.
        """
        session = self.get_session()
        async with session.client(
            "s3", endpoint_url="https://storage.googleapis.com"
        ) as s3:
            try:
                self.debug(
                    "generating presigned url", bucket=self.bucket, obj_id=obj_id
                )
                resp = await s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket, "Key": obj_id},
                    ExpiresIn=300,
                )
            except Exception:
                logger.exception("failed to generate presigned url")
                raise

        logger.info(
            "presigned url generated", bucket=self.bucket, obj_id=obj_id, resp=resp
        )

        return resp


if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--access-key")
    parser.add_argument("-s", "--access-secret")
    parser.add_argument("-p", "--fpath")
    parser.add_argument("-b", "--bucket")

    args = parser.parse_args()

    m = S3Storage(args.bucket, args.access_key, args.access_secret)

    with open(args.fpath, "rb") as f:
        image_bin = f.read()
        content = base64.b64encode(image_bin)

    print(asyncio.run(m.save(content)))
