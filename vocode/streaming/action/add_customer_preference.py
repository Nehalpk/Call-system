import aiohttp
from typing import Type, Optional, List
from pydantic.v1 import BaseModel, Field
from vocode.streaming.action.base_action import BaseAction
from vocode.streaming.models.actions import (
    ActionConfig,
    ActionInput,
    ActionOutput,
    ActionType,
)

class PutCustomerPreferencesActionConfig(ActionConfig, type=ActionType.Add_Customer_Preferences_action):
    token: str
    url: str

class PutCustomerPreferencesParameters(BaseModel):
    customer_id: str = Field(..., description="The ID of the customer")
    preference_ids: List[str] = Field(..., description="The ID(s) of the preferences to set get the ids from show all customer preferences as user selected  ")

class PutCustomerPreferencesResponse(BaseModel):
    data: Optional[dict]
    success: bool
    error: Optional[str] = None

class PutCustomerPreferencesAction(
    BaseAction[
        PutCustomerPreferencesActionConfig,
        PutCustomerPreferencesParameters,
        PutCustomerPreferencesResponse
    ]
):
    description: str = """ Add or Update customer preferences using a GraphQL mutation.
    
    Args:
    - url (str): The endpoint URL of the GraphQL API.
    - token (str): The authentication token.
    - customer_id (str): The ID of the customer.
    - preference_ids (str or list): The ID(s) of the preferences to set.
    
    Returns:
    - dict: The JSON response from the API."""
    parameters_type: Type[PutCustomerPreferencesParameters] = PutCustomerPreferencesParameters
    response_type: Type[PutCustomerPreferencesResponse] = PutCustomerPreferencesResponse

    async def execute_put_customer_preferences(self, parameters: PutCustomerPreferencesParameters) -> dict:
        # Ensure preference_ids is a string separated by commas
        preference_ids = ','.join(parameters.preference_ids)

        # Define the GraphQL mutation
        mutation = f"""
        mutation PutCustomerPreferences {{
            putCustomerPreferences(customerId: "{parameters.customer_id}", preferenceIds: "{preference_ids}")
        }}
        """

        # Set the headers with the token for authentication
        headers = {  
            "Authorization": f"Bearer {self.action_config.token}",
            "Content-Type": "application/json"
        }

        # Make the request to the GraphQL API
        async with aiohttp.ClientSession() as session:
            async with session.post(self.action_config.url, json={'query': mutation}, headers=headers) as response:
                if response.status != 200:
                    error_message = await response.text()
                    raise Exception(f"API call failed: {error_message}")
                return await response.json()

    async def run(
        self, action_input: ActionInput[PutCustomerPreferencesParameters]
    ) -> ActionOutput[PutCustomerPreferencesResponse]:
        try:
            data = await self.execute_put_customer_preferences(action_input.params)
            print ("\n\n\n\n\n\nFrom Add preferences here is the ",data)
            return ActionOutput(
                action_type=self.action_config.type,
                response=PutCustomerPreferencesResponse(success=True, data=data)
            )
        except Exception as e:
            return ActionOutput(
                action_type=self.action_config.type,
                response=PutCustomerPreferencesResponse(success=False, error=str(e))
            )
