import aiohttp
from typing import Type, Optional
from pydantic.v1 import BaseModel

from vocode.streaming.action.base_action import BaseAction
from vocode.streaming.models.actions import (
    ActionConfig,
    ActionInput,
    ActionOutput,
    ActionType,
)

# Define the ActionConfig class with the necessary fields
class ShowAllCustomerPreferencesActionConfig(ActionConfig, type=ActionType.Show_all_customer_preference):
    token: str
    url: str

# Define the Parameters class (no parameters needed for this example)
class ShowAllCustomerPreferencesParameters(BaseModel):
    pass

# Define the Response class
class ShowAllCustomerPreferencesResponse(BaseModel):
    data: Optional[dict]
    success: bool
    error: Optional[str] = None

# Implement the class to handle the query execution
class ShowAllCustomerPreferences(
    BaseAction[
        ShowAllCustomerPreferencesActionConfig,
        ShowAllCustomerPreferencesParameters,
        ShowAllCustomerPreferencesResponse
    ]
):
    description: str = "Show all customer preferences."
    parameters_type: Type[ShowAllCustomerPreferencesParameters] = ShowAllCustomerPreferencesParameters
    response_type: Type[ShowAllCustomerPreferencesResponse] = ShowAllCustomerPreferencesResponse

    async def execute_graphql_query(self, token: str, url: str) -> dict:
        query = """
        query CustomerPreferences {
            customerPreferences {
                id
                name
                options {
                    id
                    name
                }
                hideCustomerPreference
            }
        }
        """

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "query": query
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_message = await response.text()
                    raise Exception(f"API call failed: {error_message}")
                return await response.json()

    async def run(
        self, action_input: ActionInput[ShowAllCustomerPreferencesParameters]
    ) -> ActionOutput[ShowAllCustomerPreferencesResponse]:
        try:
            data = await self.execute_graphql_query(
             
                self.action_config.token,
                self.action_config.url
            )
            print ("show all customoer preferences",data)
            return ActionOutput(
                action_type=self.action_config.type,
                response=ShowAllCustomerPreferencesResponse(success=True, data=data)
            )
        except Exception as e:
            return ActionOutput(
                action_type=self.action_config.type,
                response=ShowAllCustomerPreferencesResponse(success=False, error=str(e))
            )
