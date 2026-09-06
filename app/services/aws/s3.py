from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.integrations.aws.clients import AWSClientFactory


class S3Service:
    def __init__(self):
        self.client = AWSClientFactory.create_client("s3")
        self.bucket = settings.s3_bucket_name

    async def upload(self, key: str, data: bytes, content_type: str) -> dict[str, Any]:
        import asyncio

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            ),
        )
        return {"bucket": self.bucket, "key": key}

    async def download(self, key: str) -> bytes:
        import asyncio

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.get_object(Bucket=self.bucket, Key=key),
        )
        return response["Body"].read()

    async def delete(self, key: str) -> None:
        import asyncio

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.delete_object(Bucket=self.bucket, Key=key),
        )

    async def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            ),
        )
