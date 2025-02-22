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
# import requests
# import json
# from vocode.streaming.action.execute_function import execute_graphql_query_by_Phone
# class PutAppointmentActionConfig(ActionConfig, type=ActionType.Put_Appointment):
#     token: str
#     url: str

# class PutAppointmentParameters(BaseModel):
#     phone: str = Field(..., description="The email address associated with the customer")
#     selected_date: int
#     selected_month: int
#     selected_year: int
#     time_slot_id: str

# class PutAppointmentResponse(BaseModel):
#     data: Optional[dict]
#     success: bool
#     error: Optional[str] = None

# class PutAppointmentAction(
#     BaseAction[
#         PutAppointmentActionConfig,
#         PutAppointmentParameters,
#         PutAppointmentResponse
#     ]
# ):
#     description: str = "Puts an appointment based on provided parameters "
#     parameters_type: Type[PutAppointmentParameters] = PutAppointmentParameters
#     response_type: Type[PutAppointmentResponse] = PutAppointmentResponse

#     async def execute_put_appointment(self, parameters: PutAppointmentParameters) -> dict:
#         response = execute_graphql_query_by_Phone(parameters.phone)
#         print(response)
        
#         if not response:
#             return json.dumps({"error": "No response from execute_graphql_query_by_phone"})

#         # Parse response to extract required IDs
#         appointment_id = response["data"]["business"]["getCustomer"]["id"]
#         address_id = response["data"]["business"]["getCustomer"]["addresses"][0]["id"]
#         customer_id = response["data"]["business"]["getCustomer"]["id"]
#         route_id = response["data"]["business"]["routes"][0]["id"]
#         mutation = f"""
#         mutation PutAppointment {{
#             putAppointment(
#                 input: {{
#                     id: "{appointment_id}"
#                     addressId: "{address_id}"
#                     customerId: "{customer_id}"
#                     selectedDate: {parameters.selected_date}
#                     selectedMonth: {parameters.selected_month}
#                     selectedYear: {parameters.selected_year}
#                     timeSlotId: "{parameters.time_slot_id}"
#                     routeId: "{route_id}"
#                 }}
#             ) {{
#                 id
#                 localId
#                 startTime
#                 endTime
#                 scheduledAt
#                 driverInstructions
#                 cleaningInstructions
#                 regular
#                 anytime
#                 status
#                 appointmentLinkId
#                 lockerCode
#                 locationLabel
#                 stopNumber
#             }}
#         }}
#         """
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {self.action_config.token}"
#         }
#         payload = {"query": mutation}
#         async with aiohttp.ClientSession() as session:
#             async with session.post(self.action_config.url, headers=headers, json=payload) as response:
#                 if response.status != 200:
#                     error_message = await response.text()
#                     raise Exception(f"API call failed: {error_message}")
#                 return await response.json()

#     async def run(
#         self, action_input: ActionInput[PutAppointmentParameters]
#     ) -> ActionOutput[PutAppointmentResponse]:
#         try:
#             data = await self.execute_put_appointment(action_input.params)
#             return ActionOutput(
#                 action_type=self.action_config.type,
#                 response=PutAppointmentResponse(success=True, data=data)
#             )
#         except Exception as e:
#             return ActionOutput(
#                 action_type=self.action_config.type,
#                 response=PutAppointmentResponse(success=False, error=str(e))
#             )



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

class PutAppointmentActionConfig(ActionConfig, type=ActionType.Put_Appointment):
    token: str
    url: str

class PutAppointmentParameters(BaseModel):
    phone: str = Field(..., description="The phone number associated with the customer")
    selected_date: int
    selected_month: int
    selected_year: int
    time_slot_id: int 
    cleaningInstructions: Optional[str] = Field(None, description="Always ask Instructions for cleaning")
    driverInstructions: Optional[str] = Field(None, description="Instructions for the driver")
    routeId: Optional[str] = Field(None, description="Route ID for the appointment")
    lockerCode: Optional[str] = Field(None, description="Locker code for the appointment")

class PutAppointmentResponse(BaseModel):
    data: Optional[dict]
    success: bool
    error: Optional[str] = None

class PutAppointmentAction(
    BaseAction[
        PutAppointmentActionConfig,
        PutAppointmentParameters,
        PutAppointmentResponse
    ]
):
    description: str = "Puts an appointment based on provided parameters also always pass time slot id as integer in time_slot_id also always ask about cleaning instructions and driver instructions"
    parameters_type: Type[PutAppointmentParameters] = PutAppointmentParameters
    response_type: Type[PutAppointmentResponse] = PutAppointmentResponse

    async def execute_put_appointment(self, parameters: PutAppointmentParameters) -> dict:
        response = execute_graphql_query_by_Phone(parameters.phone)
        print(response)
        
        if not response:
            return json.dumps({"error": "No response from execute_graphql_query_by_phone"})

        # Parse response to extract required IDs
        appointment_id = response["data"]["business"]["getCustomer"]["id"]
        address_id = response["data"]["business"]["getCustomer"]["addresses"][0]["id"]
        customer_id = response["data"]["business"]["getCustomer"]["id"]
        route_id = response["data"]["business"]["routes"][0]["id"] if not parameters.routeId else parameters.routeId
        
        mutation = f"""
        mutation PutAppointment {{
            putAppointment(
                input: {{
                    id: "{appointment_id}"
                    addressId: "{address_id}"
                    customerId: "{customer_id}"
                    selectedDate: {parameters.selected_date}
                    selectedMonth: {parameters.selected_month}
                    selectedYear: {parameters.selected_year}
                    timeSlotId: "{parameters.time_slot_id}"
                    routeId: "{route_id}"
                    cleaningInstructions: "{parameters.cleaningInstructions or ''}"
                    driverInstructions: "{parameters.driverInstructions or ''}"
                    lockerCode: "{parameters.lockerCode or ''}"
                }}
            ) {{
                id
                localId
                startTime
                endTime
                scheduledAt
                driverInstructions
                cleaningInstructions
                regular
                anytime
                status
                appointmentLinkId
                lockerCode
                locationLabel
                stopNumber
            }}
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
        self, action_input: ActionInput[PutAppointmentParameters]
    ) -> ActionOutput[PutAppointmentResponse]:
        try:
            data = await self.execute_put_appointment(action_input.params)
            return ActionOutput(
                action_type=self.action_config.type,
                response=PutAppointmentResponse(success=True, data=data)
            )
        except Exception as e:
            return ActionOutput(
                action_type=self.action_config.type,
                response=PutAppointmentResponse(success=False, error=str(e))
            )
