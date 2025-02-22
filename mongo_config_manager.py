import logging
import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from vocode.streaming.models.telephony import BaseCallConfig
from vocode.streaming.telephony.config_manager.base_config_manager import (
    BaseConfigManager,
)


class MongoDBConfigManager(BaseConfigManager):
    def __init__(self, logger: Optional[logging.Logger] = None):
        mongo_uri = os.environ.get("MONGO_DB_URL", "mongodb+srv://faisalqazi31:QWcJl6ybdwSKLwvp@ai-lead-generation-clus.dvybt5d.mongodb.net/?retryWrites=true&w=majority&appName=ai-lead-generation-cluster0")
        db_name = os.environ.get("MONGO_DB_NAME", "test")
        collection_name = os.environ.get("COLLECTION_NAME", "call_cfg")
        
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.logger = logger or logging.getLogger(__name__)

    async def save_config(self, conversation_id: str, config: BaseCallConfig):
        self.logger.debug(f"Saving config for {conversation_id}")
        await self.collection.update_one(
            {"conversation_id": conversation_id},
            {"$set": {"config": config.json()}},
            upsert=True
        )

    async def get_config(self, conversation_id: str) -> Optional[BaseCallConfig]:
        self.logger.debug(f"Getting config for {conversation_id}")
        raw_config = await self.collection.find_one({"conversation_id": conversation_id})
        if raw_config and "config" in raw_config:
            return BaseCallConfig.parse_raw(raw_config["config"])
        return None
    

    async def delete_config(self, conversation_id: str):
        self.logger.debug(f"Deleting config for {conversation_id}")
        await self.collection.delete_one({"conversation_id": conversation_id})
