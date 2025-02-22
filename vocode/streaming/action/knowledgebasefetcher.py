# import aiohttp
# from typing import Type, Optional
# from pydantic.v1 import BaseModel, Field
# from vocode.streaming.action.base_action import BaseAction
# from vocode.streaming.models.actions import (
#     ActionConfig,
#     ActionInput,
#     ActionOutput,
#     ActionType,
# )
# import json

# class QueryActionConfig(ActionConfig, type=ActionType.Query_Action):
#     url: str
#     index_name: str 
# class QueryParameters(BaseModel):
#     query: str = Field(..., description="The query to search for")
    

# class QueryResponse(BaseModel):
#     data: Optional[dict]
#     success: bool
#     error: Optional[str] = None

# class QueryAction(
#     BaseAction[
#         QueryActionConfig,
#         QueryParameters,
#         QueryResponse
#     ]
# ):
#     description: str = "Executes a query based on the query string and index_name provided"
#     parameters_type: Type[QueryParameters] = QueryParameters
#     response_type: Type[QueryResponse] = QueryResponse

#     async def execute_query(self, parameters: QueryParameters) -> dict:
#         query_payload = {
#             "query": parameters.query,
#             "index_name": self.action_config.index_name
#         }
        
#         headers = {
#             "accept": "application/json",
#             "Content-Type": "application/json"
#         }
        
#         async with aiohttp.ClientSession() as session:
#             async with session.post(self.action_config.url, headers=headers, json=query_payload) as response:
#                 if response.status != 200:
#                     error_message = await response.text()
#                     raise Exception(f"API call failed: {error_message}")
#                 return await response.json()

#     async def run(
#         self, action_input: ActionInput[QueryParameters]
#     ) -> ActionOutput[QueryResponse]:
#         try:
#             data = await self.execute_query(action_input.params)
#             return ActionOutput(
#                 action_type=self.action_config.type,
#                 response=QueryResponse(success=True, data=data)
#             )
#         except Exception as e:
#             return ActionOutput(
#                 action_type=self.action_config.type,
#                 response=QueryResponse(success=False, error=str(e))
#             )










#import aiohttp
#from typing import Type, Optional
#from pydantic.v1 import BaseModel, Field
#from vocode.streaming.action.base_action import BaseAction
#from vocode.streaming.models.actions import (
#    ActionConfig,
#    ActionInput,
#    ActionOutput,
#    ActionType,
#)
#import json
#
#class QueryActionConfig(ActionConfig, type=ActionType.Query_Action):
#    url: str
#    index_name: str 
#class QueryParameters(BaseModel):
#    query: str = Field(..., description="The query to search for")
#    
#
#class QueryResponse(BaseModel):
#    data: Optional[dict]
#    success: bool
#    error: Optional[str] = None
#
#class QueryAction(
#    BaseAction[
#        QueryActionConfig,
#        QueryParameters,
#        QueryResponse
#    ]
#):
#    description: str = "Executes a query based on the query string and index_name provided"
#    parameters_type: Type[QueryParameters] = QueryParameters
#    response_type: Type[QueryResponse] = QueryResponse
#
#    async def execute_query(self, parameters: QueryParameters) -> dict:
#        query_payload = {
#            "query": parameters.query,
#            "index_name": self.action_config.index_name
#        }
#        
#        headers = {
#            "accept": "application/json",
#            "Content-Type": "application/json"
#        }
#        
#        async with aiohttp.ClientSession() as session:
#            async with session.post(self.action_config.url, headers=headers, json=query_payload) as response:
#                if response.status != 200:
#                    error_message = await response.text()
#                    print (f"API call failed: {error_message}")
#                    raise Exception(f"API call failed: {error_message}")
#                return await response.json()
#
#    async def run(
#        self, action_input: ActionInput[QueryParameters]
#    ) -> ActionOutput[QueryResponse]:
#        try:
#            data = await self.execute_query(action_input.params)
#            return ActionOutput(
#                action_type=self.action_config.type,
#                response=QueryResponse(success=True, data=data)
#                
#            )
#        except Exception as e:
#            return ActionOutput(
#                action_type=self.action_config.type,
#                response=QueryResponse(success=False, error=str(e))
#            )
#





import aiohttp
import json
from typing import Type, Optional
from pydantic import BaseModel, Field
from vocode.streaming.action.base_action import BaseAction
from vocode.streaming.models.actions import (
    ActionConfig,
    ActionInput,
    ActionOutput,
    ActionType,
)
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryActionConfig(ActionConfig, type=ActionType.Query_Action):
    url: str
    index_name: str

class QueryParameters(BaseModel):
    query: str = Field(..., description="The query to search for")

class QueryResponse(BaseModel):
    data: Optional[dict]
    success: bool
    error: Optional[str] = None

class QueryAction(
    BaseAction[
        QueryActionConfig,
        QueryParameters,
        QueryResponse
    ]
):
    description: str = "Executes a query based on the query"
    parameters_type: Type[QueryParameters] = QueryParameters
    response_type: Type[QueryResponse] = QueryResponse

    async def execute_query(self, parameters: QueryParameters) -> dict:
       query_payload = {
           "query": parameters.query,
           "index_name": self.action_config.index_name
       }
       headers = {
           "Content-Type": "application/json"
       }
   
       logger.info(f"Sending request to {self.action_config.url}")
       logger.info(f"Headers: {headers}")
       logger.info(f"Payload: {json.dumps(query_payload)}")
   
       async with aiohttp.ClientSession() as session:
           try:
               async with aiohttp.ClientSession() as session:
                  async with session.post(self.action_config.url, headers=headers, json=query_payload, ssl=False) as response:

            #    async with session.post(self.action_config.url, headers=headers, json=query_payload) as response:
                   response_text = await response.text()
                   logger.info(f"Response status: {response.status}")
                   logger.info(f"Response headers: {response.headers}")
                   logger.info(f"Response body: {response_text}")
   
                   if response.status != 200:
                       raise Exception(f"API call failed: Status {response.status}, Message: {response_text}")
   
                   return await response.json()
           except aiohttp.ClientError as e:
               logger.error(f"Network error occurred: {str(e)}")
               raise

    async def run(
        self, action_input: ActionInput[QueryParameters]
    ) -> ActionOutput[QueryResponse]:
        try:
            data = await self.execute_query(action_input.params)
            return ActionOutput(
                action_type=self.action_config.type,
                response=QueryResponse(success=True, data=data)
            )
        except Exception as e:
            logger.error(f"Error in QueryAction: {str(e)}", exc_info=True)
            return ActionOutput(
                action_type=self.action_config.type,
                response=QueryResponse(success=False, error=str(e))
            )

# # Example usage
# if __name__ == "__main__":
#     import asyncio

#     async def main():
#         config = QueryActionConfig(
#             type=ActionType.Query_Action,
#             url="https://ai-lead-generation-nodejs.onrender.com/pinecone/query",
#             index_name="66ee62824e560426c2514dae"
#         )
#         action = QueryAction(action_config=config)
#         input_params = QueryParameters(query="Octaloop Technologies")
#         result = await action.run(ActionInput(params=input_params))
#         print(result)

#     asyncio.run(main())
