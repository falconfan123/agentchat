import os
import io
import uuid
import shutil
from pathlib import Path
from loguru import logger
from agentchat.settings import app_settings


class LocalStorageClient:
    """本地存储客户端 - 用于替代 MinIO/OSS"""

    def __init__(self):
        self.base_path = Path(app_settings.storage.local.base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.bucket_name = "agentchat"
        self.bucket_path = self.base_path / self.bucket_name
        self.bucket_path.mkdir(parents=True, exist_ok=True)
        logger.success(f"Local storage initialized: {self.bucket_path}")

    def _get_full_path(self, object_name):
        """获取对象的完整路径"""
        return self.bucket_path / object_name

    def upload_file(self, object_name, data):
        """上传文件内容"""
        try:
            full_path = self._get_full_path(object_name)
            full_path.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(data, (bytes, bytearray)):
                full_path.write_bytes(data)
            else:
                data = data.encode("utf-8") if isinstance(data, str) else data
                full_path.write_bytes(data)

            logger.info(f"File uploaded successfully: {object_name}")
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")

    def upload_local_file(self, object_name, local_file):
        """上传本地文件"""
        try:
            full_path = self._get_full_path(object_name)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(local_file, full_path)
            logger.info(f"Local file uploaded successfully: {object_name}")
        except Exception as e:
            logger.error(f"Failed to upload local file: {e}")

    def delete_bucket(self):
        """删除存储桶"""
        try:
            shutil.rmtree(self.bucket_path)
            logger.info("Bucket deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete bucket: {e}")

    def sign_url_for_get(self, object_name, expiration=3600):
        """生成下载链接（本地存储返回本地路径）"""
        try:
            full_path = self._get_full_path(object_name)
            if full_path.exists():
                return str(full_path)
            return None
        except Exception as e:
            logger.error(f"Failed to generate GET URL for {object_name}: {e}")

    def download_file(self, object_name, local_file):
        """下载文件"""
        try:
            full_path = self._get_full_path(object_name)
            if full_path.exists():
                shutil.copy2(full_path, local_file)
                logger.info(f"File {object_name} downloaded successfully to {local_file}")
            else:
                logger.error(f"File {object_name} does not exist")
        except Exception as e:
            logger.error(f"Failed to download {object_name} to {local_file}: {e}")

    def list_files_in_folder(self, folder_path):
        """列出指定文件夹下的所有文件"""
        try:
            folder = self.bucket_path / folder_path
            if not folder.exists():
                return []

            files = []
            for f in folder.iterdir():
                if f.is_file():
                    files.append(str(f.relative_to(self.bucket_path)))

            return files
        except Exception as e:
            logger.error(f"Failed to list files in folder {folder_path}: {e}")
            return []