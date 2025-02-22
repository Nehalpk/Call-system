import asyncio
from enum import Enum
from typing import Generic, Optional, TypeVar
from pydantic.v1 import BaseModel
from vocode.streaming.models.model import TypedModel


class ActionType(str, Enum):
    # BASE = "action_base"
    # NYLAS_SEND_EMAIL = "action_nylas_send_email"
    # TRANSFER_CALL = "action_transfer_call"
    Query_Action="action_query"
    BASE = "action_base"
    NYLAS_SEND_EMAIL = "action_nylas_send_email"
    TRANSFER_CALL = "action_transfer_call"
    GRAPHQL_QUERY_BY_PHONE ="action_graphql_query_by_phone"
    SEND_OTP="Send_Otp_to_verify"
    Put_Appointment = "put_appointment_action"
    FETCH_OPTIONS_BY_IDS= "Get_customer_preference_by_id"
    Add_Customer_Preferences_action ="add_customer_preferences_action"
    Show_all_customer_preference="show_all_customer_preference"
    Send_Email_Action ="send_email_action"
class ActionConfig(TypedModel, type=ActionType.BASE):
    pass


ParametersType = TypeVar("ParametersType", bound=BaseModel)


class ActionInput(BaseModel, Generic[ParametersType]):
    action_config: ActionConfig
    conversation_id: str
    params: ParametersType
    user_message_tracker: Optional[asyncio.Event] = None

    class Config:
        arbitrary_types_allowed = True


class FunctionFragment(BaseModel):
    name: str
    arguments: str


class FunctionCall(BaseModel):
    name: str
    arguments: str


class VonagePhoneCallActionInput(ActionInput[ParametersType]):
    vonage_uuid: str


class TwilioPhoneCallActionInput(ActionInput[ParametersType]):
    twilio_sid: str


ResponseType = TypeVar("ResponseType", bound=BaseModel)


class ActionOutput(BaseModel, Generic[ResponseType]):
    action_type: str
    response: ResponseType
