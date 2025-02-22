from pydantic import BaseModel, ValidationError
from typing import Any, List
from mongodb_config.mongo_db_config import mongo_handler
from Utilitiess.utils import convert_to_string
# Define Pydantic models
class InboundCallConfigRequest(BaseModel):
    Agent_id: str

class AgentPersonalData(BaseModel):
    AgentName: str 
    CompanyName: str
    CompanyBusiness: str
    livetransfer: str
    customerID: str
    greetings: str 
    audioId: str

class AgentKeysData(BaseModel):
    openAI: str
    ElevenLabs: str
    accountSID: str
    authtoken: str

class KnowledgeBaseData(BaseModel):
    data: List[Any]

# Helper functions
async def fetch_agent_personal_data(agent_id: str) -> AgentPersonalData:
    agent_personal_data = mongo_handler.get_data_from_db_by_obj_ID("agents", agent_id)
    return AgentPersonalData(**agent_personal_data)

async def fetch_agent_keys_data(customer_id: str) -> AgentKeysData:
    agent_keys_data = mongo_handler.get_data_by_key_and_value("agentkeys", "customerID", customer_id)
    return AgentKeysData(**agent_keys_data)

async def fetch_knowledge_base_data(agent_id: str) -> str:
    knowledge_base_data = mongo_handler.get_all_data_by_array_value("knowledges", "AgentID", agent_id)
    validated_data = KnowledgeBaseData(data=knowledge_base_data)
    return convert_to_string(validated_data.data)
