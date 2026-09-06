from __future__ import annotations

from typing import Any

import boto3
from botocore.client import BaseClient

from app.core.config import settings


class AWSClientFactory:
    @staticmethod
    def _client_kwargs(service_name: str) -> dict[str, Any]:
        return {
            "service_name": service_name,
            "region_name": settings.AWS_REGION,
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "endpoint_url": settings.AWS_ENDPOINT_URL,
        }

    @classmethod
    def create_client(cls, service_name: str) -> BaseClient:
        return boto3.client(**cls._client_kwargs(service_name))

    @classmethod
    def create_resource(cls, service_name: str):
        return boto3.resource(**cls._client_kwargs(service_name))
