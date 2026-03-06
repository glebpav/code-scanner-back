from typing import Dict, Any, Optional
import aioboto3
from botocore.config import Config


class S3Client:
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
            region_name: str,
            verify_tls: bool = True,
            force_path_style: bool = True,
    ):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url

        # Important for many S3-compatible providers:
        # - signature_version='s3v4' is standard
        # - addressing_style='path' avoids DNS/virtual-host quirks
        s3_cfg = {}
        if force_path_style:
            s3_cfg["addressing_style"] = "path"

        self._boto_config = Config(
            signature_version="s3v4",
            s3=s3_cfg,
        )

        self.session = aioboto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name,
        )
        self.verify_tls = verify_tls

    async def upload_file(
            self,
            file_path: str,
            object_key: str,
            content_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:

        try:
            async with self.session.client(
                    "s3",
                    endpoint_url=self.endpoint_url,
                    verify=self.verify_tls,
                    config=self._boto_config,
            ) as s3:
                await s3.upload_file(
                    file_path,
                    self.bucket_name,
                    object_key,
                    ExtraArgs={'ContentType': content_type}
                )
            return {"success": True}
        except Exception as e:
            return {
                "success": False,
                "error_msg": str(e)
            }

    async def get_download_url(
            self,
            object_key: str,
            expiration: int = 3600
    ) -> Dict[str, Any]:
        try:
            async with self.session.client(
                    "s3",
                    endpoint_url=self.endpoint_url,
                    verify=self.verify_tls,
                    config=self._boto_config,
            ) as s3:
                try:
                    await s3.head_object(
                        Bucket=self.bucket_name,
                        Key=object_key
                    )
                except s3.exceptions.ClientError as e:
                    if e.response['Error']['Code'] in ['404', 'NoSuchKey']:
                        return {
                            "success": False,
                            "error_msg": f"File {object_key} is not found"
                        }
                    raise

                url = await s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': object_key},
                    ExpiresIn=expiration
                )

                return {
                    "success": True,
                    "result": url
                }

        except Exception as e:
            return {
                "success": False,
                "error_msg": str(e)
            }

    async def download_file(self, object_key: str) -> Dict[str, Any]:
        try:
            async with self.session.client(
                    "s3",
                    endpoint_url=self.endpoint_url,
                    verify=self.verify_tls,
                    config=self._boto_config,
            ) as s3:
                try:
                    await s3.head_object(Bucket=self.bucket_name, Key=object_key)
                except s3.exceptions.ClientError as e:
                    if e.response['Error']['Code'] in ['404', 'NoSuchKey']:
                        return {
                            "success": False,
                            "error_msg": f"File {object_key} not found"
                        }
                    raise

                response = await s3.get_object(Bucket=self.bucket_name, Key=object_key)
                file_data = await response['Body'].read()
                return {
                    "success": True,
                    "result": file_data
                }

        except Exception as e:
            return {
                "success": False,
                "error_msg": str(e)
            }
