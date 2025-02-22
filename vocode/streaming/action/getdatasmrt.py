import os
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

# Update class name to reflect phone usage
class ExecuteGraphQLQueryByPhoneActionConfig(ActionConfig, type=ActionType.GRAPHQL_QUERY_BY_PHONE):
    token: str
    url: str

# Change email to phone in the parameters
class ExecuteGraphQLQueryByPhoneParameters(BaseModel):
    phone: str = Field(..., description="The phone number to query.")

# No changes needed for the response class
class ExecuteGraphQLQueryByPhoneResponse(BaseModel):
    data: Optional[dict]
    success: bool
    error: Optional[str] = None

# Update class name to reflect phone usage
class ExecuteGraphQLQueryByPhone(
    BaseAction[
        ExecuteGraphQLQueryByPhoneActionConfig,
        ExecuteGraphQLQueryByPhoneParameters,
        ExecuteGraphQLQueryByPhoneResponse
    ]
):
    description: str = """use when you need to get data from phone number or if he ask to tell their details like 
                    name
                    driverInstructions
                    preferences
                    goodOnlineAccountStanding
                    creditCardIFrameURL
                    authenticatedCustomerSiteLink
                    isRouteCustomer
                    customerRelationship
                    deliveryStop
                    demographic   """
    parameters_type: Type[ExecuteGraphQLQueryByPhoneParameters] = ExecuteGraphQLQueryByPhoneParameters
    response_type: Type[ExecuteGraphQLQueryByPhoneResponse] = ExecuteGraphQLQueryByPhoneResponse

    # Adjust method name to reflect phone usage
    async def execute_graphql_query(self, phone: str, token: str, url: str) -> dict:
        # query = f"""
        # query Business {{
        #     business {{
        #         getCustomer(by: phone, term: "{phone}") {{
        #             id
        #             localId
        #             name
        #             driverInstructions
        #             preferences
        #             goodOnlineAccountStanding
        #             creditCardIFrameURL
        #             authenticatedCustomerSiteLink
        #             isRouteCustomer
        #             customerRelationship
        #             deliveryStop
        #             demographic
        #             apiTokenForCustomer
        #             kioskAccessCode
        #             email
        #             cellPhone
        #             cellPhoneDisplay
        #             homePhone
        #             activePhone
        #             firstName
        #             lastName
        #             companyName
        #             fullName
        #             isInSignupProcess
        #             paymentPreference
        #             rewardPoints
        #             missingRewardSettingCriteria
        #             isSubBilling
        #             addresses {{
        #                 id
        #                 localId
        #                 name
        #                 streetAddress
        #                 streetAddress2
        #                 city
        #                 state
        #                 zip
        #                 country
        #                 latitude
        #                 longitude
        #                 skipVerification
        #                 manualLocation
        #                 note
        #             }}
        #             futureAppointments {{
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
        #             routeHolds {{
        #                 id
        #                 localId
        #                 startDate
        #                 endDate
        #             }}
        #             subscription {{
        #                 id
        #                 localId
        #                 renewalDate
        #                 pending {{
        #                     id
        #                     localId
        #                     saleId
        #                     price
        #                     start
        #                     end
        #                 }}
        #                 active {{
        #                     id
        #                     localId
        #                     saleId
        #                     price
        #                     start
        #                     end
        #                 }}
        #                 log {{
        #                     id
        #                     localId
        #                     date
        #                     event
        #                     description
        #                 }}
        #             }}
        #             store {{
        #                 id
        #                 localId
        #                 agentId
        #                 agentType
        #                 name
        #                 isStripeEnabled
        #                 phone
        #                 address
        #                 city
        #                 state
        #                 zip
        #                 latitude
        #                 longitude
        #                 externalStoreIdentifier
        #                 googlePlaceId
        #                 hasCounterStation
        #             }}
        #             customFields {{
        #                 id
        #                 localId
        #                 label
        #                 value
        #             }}
        #         }}
        #         routes {{
        #             id
        #             localId
        #             agentId
        #             agentType
        #             name
        #             isStripeEnabled
        #             type
        #             isSubRoute
        #             masterRouteId
        #             pickupCutoffHours
        #             deliveryCutoffHours
        #             autoOptimize
        #         }}
        #     }}
        # }}
        # """

        query = f"""
        query Business {{
            business {{
                getCustomer(by: phone, term: "{phone}") {{  
                    id
                    localId
                    name
                    driverInstructions
                    preferences
                    goodOnlineAccountStanding
                    creditCardIFrameURL
                    authenticatedCustomerSiteLink
                    isRouteCustomer
                    customerRelationship
                    deliveryStop
                    demographic
                    apiTokenForCustomer
                    kioskAccessCode
                    email
                    cellPhone
                    cellPhoneDisplay
                    homePhone
                    activePhone
                    firstName
                    lastName
                    companyName
                    fullName
                    isInSignupProcess
                    paymentPreference
                    rewardPoints
                    missingRewardSettingCriteria
                    isSubBilling
                    settings {{
                        id
                        localId
                        logo
                        receiptLogo
                        POSNewOrderTabs
                        isLockers
                     }}
                    addresses {{
                        id
                        localId
                        name
                        streetAddress
                        streetAddress2
                        city
                        state
                        zip
                        country
                        latitude
                        longitude
                        skipVerification
                        manualLocation
                        note
                    }}
                    futureAppointments {{
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
                    
                    routeHolds {{
                        id
                        localId
                        startDate
                        endDate
                    }}
                    subscription {{
                        id
                        localId
                        renewalDate
                        pending {{
                            id
                            localId
                            saleId
                            price
                            start
                            end
                        }}
                        active {{
                            id
                            localId
                            saleId
                            price
                            start
                            end
                        }}
                        log {{
                            id
                            localId
                            date
                            event
                            description
                        }}
                    }}
                    store {{
                        id
                        localId
                        agentId
                        agentType
                        name
                        isStripeEnabled
                        phone
                        address
                        city
                        state
                        zip
                        latitude
                        longitude
                        externalStoreIdentifier
                        googlePlaceId
                        hasCounterStation
                    }}
                    customFields {{
                        id
                        localId
                        label
                        value
                    }}
                }}
            lockers {{
            id
            localId
            address {{
                id
                localId
                name
                streetAddress
                streetAddress2
                city
                state
                zip
                country
                latitude
                longitude
                skipVerification
                manualLocation
                note
            }}
        }}
                routes {{
                    id
                    localId
                    agentId
                    agentType
                    name
                    isStripeEnabled
                    type
                    isSubRoute
                    masterRouteId
                    pickupCutoffHours
                    deliveryCutoffHours
                    autoOptimize
                }}
            }}
            
        }}
        """

        
        
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        payload = {
            "query": query
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_message = await response.text()
                    raise Exception(f"API call failed: {error_message}")
                print (response.json())
                return await response.json()

    async def run(
        self, action_input: ActionInput[ExecuteGraphQLQueryByPhoneParameters]
    ) -> ActionOutput[ExecuteGraphQLQueryByPhoneResponse]:
        try:
            data = await self.execute_graphql_query(
                action_input.params.phone,
                self.action_config.token,
                self.action_config.url
            )
            return ActionOutput(
                action_type=self.action_config.type,
                response=ExecuteGraphQLQueryByPhoneResponse(success=True, data=data)
            )
        except Exception as e:
            return ActionOutput(
                action_type=self.action_config.type,
                response=ExecuteGraphQLQueryByPhoneResponse(success=False, error=str(e))
            )
