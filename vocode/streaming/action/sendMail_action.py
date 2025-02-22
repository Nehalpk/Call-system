import aiohttp
from typing import Type, Optional
from pydantic.v1 import BaseModel, Field
from vocode.streaming.action.base_action import BaseAction
from vocode.streaming.models.actions import (
    ActionConfig,
    ActionInput,
    ActionOutput,
    ActionType,
)
import json
from vocode.streaming.action.execute_function import execute_graphql_query_by_Phone
# Step 1: Create a configuration class for the action
class SendContactLogEmailActionConfig(ActionConfig, type=ActionType.Send_Email_Action):
    token: str
    url: str = "https://apitesting.smrtapp.com/graphql"

# Step 2: Define the parameters class
class SendContactLogEmailParameters(BaseModel):
    # customer_id: str = Field(..., description="Unique identifier for the customer")
    # subject: str = Field(..., description="Subject of the email")
    # message: str = Field(..., description="Content of the email message")
    phone: str = Field(..., description="The phone number to get the customer id to send email.")
# Step 3: Define the response class
class SendContactLogEmailResponse(BaseModel):
    data: Optional[dict] = None
    success: bool
    error: Optional[str] = None

# Step 4: Create the action class
class SendContactLogEmailAction(
    BaseAction[
        SendContactLogEmailActionConfig,
        SendContactLogEmailParameters,
        SendContactLogEmailResponse
    ]
):
    description: str = "Sends an email"
    parameters_type: Type[SendContactLogEmailParameters] = SendContactLogEmailParameters
    response_type: Type[SendContactLogEmailResponse] = SendContactLogEmailResponse

    async def execute_send_contact_log_email(self, parameters: SendContactLogEmailParameters) -> dict:
        
        response = execute_graphql_query_by_Phone(parameters.phone)
        print(response)
        
        if not response:
            return json.dumps({"error": "No response from execute_graphql_query_by_phone"})

        # Parse response to extract required IDs
        # appointment_id = response["data"]["business"]["getCustomer"]["id"]
        # address_id = response["data"]["business"]["getCustomer"]["addresses"][0]["id"]
        customer_id = response["data"]["business"]["getCustomer"]["id"]
        # route_id = response["data"]["business"]["routes"][0]["id"] if not parameters.routeId else parameters.routeId
        
        authenticatedCustomerSiteLink = response["data"]["business"]["getCustomer"]["authenticatedCustomerSiteLink"]
        fullName = response["data"]["business"]["getCustomer"]["fullName"]
        
        print ()
        mutation = f"""
        mutation {{
            putContactLogEmail(
                customerId: "{customer_id}",
                subject: "Hi {fullName} You can update your Requirement here.",
                message: "Here is the link: {authenticatedCustomerSiteLink}"
            ) 
        }}
        """
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.action_config.token}"
        }
        payload = {"query": mutation}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.action_config.url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_message = await response.text()
                    raise Exception(f"API call failed: {error_message}")
                return await response.json()

    async def run(
        self, action_input: ActionInput[SendContactLogEmailParameters]
    ) -> ActionOutput[SendContactLogEmailResponse]:
        try:
            data = await self.execute_send_contact_log_email(action_input.params)
            return ActionOutput(
                action_type=self.action_config.type,
                response=SendContactLogEmailResponse(success=True, data=data)
            )
        except Exception as e:
            return ActionOutput(
                action_type=self.action_config.type,
                response=SendContactLogEmailResponse(success=False, error=str(e))
            )

# Example usage:
# config = SendContactLogEmailActionConfig(token="your_token_here")
# params = SendContactLogEmailParameters(customer_id="Customer_1033_7vvllvqjs", subject="Test Email", message="How are you my friend?")
# action_input = ActionInput(params=params)
# action = SendContactLogEmailAction(action_config=config)
# result = await action.run(action_input)
# print(result.response)
