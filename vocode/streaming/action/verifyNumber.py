import os
import random
from typing import Type, Optional
from pydantic.v1 import BaseModel, Field
from twilio.rest import Client

from vocode.streaming.action.base_action import BaseAction
from vocode.streaming.models.actions import (
    ActionConfig,
    ActionInput,
    ActionOutput,
    ActionType,
)


class SendOTPActionConfig(ActionConfig, type=ActionType.SEND_OTP):
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str


class SendOTPParameters(BaseModel):
    phone_number: str = Field(..., description="The phone number to send OTP to.")


class SendOTPResponse(BaseModel):
    success: bool
    otp: Optional[str] = None
    error: Optional[str] = None


class SendOTP(
    BaseAction[
        SendOTPActionConfig,
        SendOTPParameters,
        SendOTPResponse
    ]
):
    description: str = "use when you need to send an OTP to a phone number Or verify a phone Number dont tell otp to anyone just match and tell true or false."
    parameters_type: Type[SendOTPParameters] = SendOTPParameters
    response_type: Type[SendOTPResponse] = SendOTPResponse

    def generate_otp(self) -> str:
        return str(random.randint(100000, 999999))

    def send_otp(self, phone_number: str, otp: str, twilio_account_sid: str, twilio_auth_token: str, twilio_phone_number: str) -> str:
        client = Client(twilio_account_sid, twilio_auth_token)
        message = client.messages.create(
            body=f'Your OTP is {otp}',
            from_=twilio_phone_number,
            to=phone_number
        )
        return message.sid

    async def run(
        self, action_input: ActionInput[SendOTPParameters]
    ) -> ActionOutput[SendOTPResponse]:
        try:
            otp = self.generate_otp()
            sid = self.send_otp(
                action_input.params.phone_number,
                otp,
                self.action_config.twilio_account_sid,
                self.action_config.twilio_auth_token,
                self.action_config.twilio_phone_number
            )
            print(f'OTP sent to {action_input.params.phone_number}. SID: {sid}')
            return ActionOutput(
                action_type=self.action_config.type,
                response=SendOTPResponse(success=True, otp=otp)
            )
        except Exception as e:
            return ActionOutput(
                action_type=self.action_config.type,
                response=SendOTPResponse(success=False, error=str(e))
            )
































# import os
# import random
# from typing import Type, Optional
# from pydantic.v1 import BaseModel, Field
# from twilio.rest import Client

# from vocode.streaming.action.base_action import BaseAction
# from vocode.streaming.models.actions import (
#     ActionConfig,
#     ActionInput,
#     ActionOutput,
#     ActionType,
# )


# class SendOTPActionConfig(ActionConfig, type=ActionType.SEND_OTP):
#     twilio_account_sid: str
#     twilio_auth_token: str
#     twilio_phone_number: str


# class SendOTPParameters(BaseModel):
#     phone_number: str = Field(..., description="The phone number to send OTP to.")


# class SendOTPResponse(BaseModel):
#     success: bool
#     error: Optional[str] = None


# class SendOTP(
#     BaseAction[
#         SendOTPActionConfig,
#         SendOTPParameters,
#         SendOTPResponse
#     ]
# ):
#     description: str = "use when you need to send an OTP to a phone number"
#     parameters_type: Type[SendOTPParameters] = SendOTPParameters
#     response_type: Type[SendOTPResponse] = SendOTPResponse

#     def generate_otp(self) -> str:
#         return str(random.randint(100000, 999999))

#     def send_otp(self, phone_number: str, otp: str, twilio_account_sid: str, twilio_auth_token: str, twilio_phone_number: str) -> str:
#         client = Client(twilio_account_sid, twilio_auth_token)
#         message = client.messages.create(
#             body=f'Your OTP is {otp}',
#             from_=twilio_phone_number,
#             to=phone_number
#         )
#         return message.sid

#     async def run(
#         self, action_input: ActionInput[SendOTPParameters]
#     ) -> ActionOutput[SendOTPResponse]:
#         try:
#             otp = self.generate_otp()
#             sid = self.send_otp(
#                 action_input.params.phone_number,
#                 otp,
#                 self.action_config.twilio_account_sid,
#                 self.action_config.twilio_auth_token,
#                 self.action_config.twilio_phone_number
#             )
#             print(f'OTP sent to {action_input.params.phone_number}. SID: {sid}')
#             return ActionOutput(
#                 action_type=self.action_config.type,
#                 response=SendOTPResponse(success=True)
#             )
#         except Exception as e:
#             return ActionOutput(
#                 action_type=self.action_config.type,
#                 response=SendOTPResponse(success=False, error=str(e))
#             )

