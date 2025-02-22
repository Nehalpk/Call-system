from vocode.streaming.action.base_action import BaseAction
from vocode.streaming.action.nylas_send_email import (
    NylasSendEmail,
    NylasSendEmailActionConfig,
)
from vocode.streaming.models.actions import ActionConfig
from vocode.streaming.action.transfer_call import TransferCall, TransferCallActionConfig
from vocode.streaming.action.getdatasmrt import ExecuteGraphQLQueryByPhone,ExecuteGraphQLQueryByPhoneActionConfig
from vocode.streaming.action.verifyNumber import SendOTP,SendOTPActionConfig
from vocode.streaming.action.createAppointment import PutAppointmentAction,PutAppointmentActionConfig
from vocode.streaming.action.show_customer_preference_by_id import FetchOptionsByIdsActionConfig,FetchOptionsByIds
from vocode.streaming.action.add_customer_preference import PutCustomerPreferencesActionConfig,PutCustomerPreferencesAction
from vocode.streaming.action.show_all_customer_preferences import ShowAllCustomerPreferencesActionConfig, ShowAllCustomerPreferences
from vocode.streaming.action.sendMail_action import SendContactLogEmailActionConfig, SendContactLogEmailAction
from vocode.streaming.action.knowledgebasefetcher import QueryAction,QueryActionConfig
# class ActionFactory:
#     def create_action(self, action_config: ActionConfig) -> BaseAction:
#         if isinstance(action_config, NylasSendEmailActionConfig):
#             return NylasSendEmail(action_config, should_respond=True)
#         elif isinstance(action_config, TransferCallActionConfig):
#             return TransferCall(action_config)
#         else:
#             raise Exception("Invalid action type")




class ActionFactory:
    def create_action(self, action_config: ActionConfig) -> BaseAction:
        if isinstance(action_config, NylasSendEmailActionConfig):
            
            return NylasSendEmail(action_config, should_respond=True)
        elif isinstance(action_config, TransferCallActionConfig):
            return TransferCall(action_config)
        
        elif isinstance(action_config, ExecuteGraphQLQueryByPhoneActionConfig):
            return ExecuteGraphQLQueryByPhone(action_config)
        
        elif isinstance(action_config,PutAppointmentActionConfig):
            return PutAppointmentAction(action_config)
        
        elif isinstance(action_config,SendOTPActionConfig):
            return SendOTP(action_config)
        
        elif isinstance (action_config,FetchOptionsByIdsActionConfig):
            return FetchOptionsByIds(action_config)
        
        elif isinstance(action_config, PutCustomerPreferencesActionConfig):
            return PutAppointmentAction(action_config)
        
        elif isinstance(action_config, ShowAllCustomerPreferencesActionConfig):
            return ShowAllCustomerPreferences(action_config)
        
        elif isinstance(action_config, SendContactLogEmailActionConfig):
            return SendContactLogEmailAction(action_config)
        elif isinstance(action_config   , QueryActionConfig):
            return QueryAction(action_config)
        else:
            raise Exception("Invalid action type")