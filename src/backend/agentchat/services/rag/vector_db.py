"""
向量数据库客户端模块

提供 Milvus 向量数据库的接口实现。
当 Milvus 服务不可用时，提供空操作实现以保证系统正常运行。
"""
from typing import List
from loguru import logger

try:
    from pymilvus import MilvusClient, DataType
except ImportError:
    MilvusClient = None

from agentchat.schema.chunk import ChunkModel
from agentchat.schema.search import SearchModel
from agentchat.settings import app_settings


class MilvusDBClient:
    """Milvus 向量数据库客户端"""

    def __init__(self):
        self.client = None
        self._initialized = False
        self._init_client()

    def _init_client(self):
        """初始化 Milvus 客户端"""
        if not MilvusClient:
            logger.warning("pymilvus 未安装，跳过 Milvus 客户端初始化")
            return

        try:
            vector_db_config = app_settings.rag.vector_db or {}
            host = vector_db_config.get("host", "127.0.0.1")
            port = vector_db_config.get("port", "19530")

            # 尝试连接到 Milvus
            self.client = MilvusClient(uri=f"http://{host}:{port}")
            self._initialized = True
            logger.info(f"Milvus 客户端初始化成功: {host}:{port}")
        except Exception as e:
            logger.warning(f"Milvus 连接失败: {e}，将使用空操作实现")
            self._initialized = False

    async def insert(self, collection_name: str, chunks: List[ChunkModel]):
        """插入文档到向量库"""
        if not self._initialized or not self.client:
            logger.debug(f"Milvus 未初始化，跳过插入操作: {collection_name}")
            return

        try:
            # 获取或创建 collection
            if not self.client.has_collection(collection_name):
                # 创建简单的 schema
                schema = self.client.create_schema(auto_id=True, enable_dynamic_field=True)
                schema.add_field("id", DataType.INT64, is_primary=True)
                schema.add_field("chunk_id", DataType.VARCHAR, max_length=256)
                schema.add_field("content", DataType.VARCHAR, max_length=65535)
                schema.add_field("summary", DataType.VARCHAR, max_length=2048)
                schema.add_field("file_name", DataType.VARCHAR, max_length=512)
                schema.add_field("file_id", DataType.VARCHAR, max_length=256)
                schema.add_field("knowledge_id", DataType.VARCHAR, max_length=256)
                schema.add_field("vectors", DataType.FLOAT_VECTOR, dim=768)  # 需要根据 embedding model 调整

                self.client.create_collection(collection_name, schema)

            # 准备数据
            data = []
            for chunk in chunks:
                data.append({
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "summary": chunk.summary,
                    "file_name": chunk.file_name,
                    "file_id": chunk.file_id,
                    "knowledge_id": chunk.knowledge_id,
                })

            self.client.insert(collection_name, data)
            logger.info(f"成功插入 {len(chunks)} 个文档到 Milvus collection: {collection_name}")
        except Exception as e:
            logger.error(f"Milvus 插入失败: {e}")

    async def search(self, query: str, knowledge_id: str) -> List[SearchModel]:
        """搜索文档"""
        if not self._initialized or not self.client:
            logger.debug(f"Milvus 未初始化，返回空结果")
            return []

        try:
            # 注意：实际实现需要先对 query 进行 embedding
            # 这里返回空列表作为占位符
            logger.debug(f"Milvus 搜索: query={query}, knowledge_id={knowledge_id}")
            return []
        except Exception as e:
            logger.error(f"Milvus 搜索失败: {e}")
            return []

    async def search_summary(self, query: str, knowledge_id: str) -> List[SearchModel]:
        """搜索文档摘要"""
        # 与 search 类似，返回空列表
        return await self.search(query, knowledge_id)

    async def delete_by_file_id(self, file_id: str, knowledge_id: str):
        """根据文件 ID 删除文档"""
        if not self._initialized or not self.client:
            logger.debug(f"Milvus 未初始化，跳过删除操作")
            return

        try:
            # 删除指定文件的文档
            self.client.delete(
                collection_name=knowledge_id,
                filter=f'file_id == "{file_id}"'
            )
            logger.info(f"成功从 Milvus 删除文件: {file_id}")
        except Exception as e:
            logger.error(f"Milvus 删除失败: {e}")


# 全局客户端实例
milvus_client = MilvusDBClient()
