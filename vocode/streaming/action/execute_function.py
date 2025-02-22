import requests
import json

url = "https://apitesting.smrtapp.com/graphql"
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2FwaXRlc3Rpbmcuc21ydGFwcC5jb20iLCJpYXQiOjE3MTk5MTY5NzMsInN1YiI6ImFkbWluIn0.i1-BCUFX4Ac3yPx5Dx8v1eco12L5IV-HajK1kKZlGGo"

def execute_graphql_query_by_Phone(phone, token=token, url=url):
    """execute_graphql_query_by_Phone"""
  # Replace this with the actual email variable or input
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
                 unpaidOrders {{
                    id
                    localId
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
   


    # Define the headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Create the payload
    payload = {
        "query": query
    }

    try:
        # Make the POST request
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # Raise an exception if the request was unsuccessful
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Return the response data
        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Return None if an error occurred
    return None




# print (execute_graphql_query_by_Phone("+13185127674"))
