import nltk
nltk.download('punkt')
import logging
import os
import sys
from fastapi import FastAPI, HTTPException,Request,WebSocket,WebSocketDisconnect, Query,WebSocketException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig, PunctuationEndpointingConfig
from pyngrok import ngrok
from Utilitiess.utils import *
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.models.agent import ChatGPTAgentConfig,CutOffResponse
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig
#from vocode.streaming.telephony.config_manager.redis_config_manager import RedisConfigManager
from vocode.streaming.telephony.server.base import TelephonyServer, TwilioInboundCallConfig
from mongo_config_manager import MongoDBConfigManager
from mongodb_config.mongo_db_config import mongo_handler
from Utilitiess.prompt import generate_prompt
# from Pydantics_base_configs.Base_configs_pydentics import InboundCallConfigRequest
from fastapi.routing import APIRoute
from Pydantics_base_configs.add_inbound_config_pydantic import *
from vocode.streaming.action.transfer_call import  TransferCallActionConfig
from pydantic import BaseModel, ValidationError
from typing import Any, List
from vocode.streaming.action.getdatasmrt import ExecuteGraphQLQueryByPhoneActionConfig
from vocode.streaming.action.createAppointment import PutAppointmentActionConfig
from vocode.streaming.action.getdatasmrt import ExecuteGraphQLQueryByPhoneActionConfig
from vocode.streaming.action.createAppointment import PutAppointmentActionConfig
from vocode.streaming.action.show_customer_preference_by_id import FetchOptionsByIdsActionConfig
from vocode.streaming.action.add_customer_preference import PutCustomerPreferencesActionConfig
from vocode.streaming.action.show_all_customer_preferences import ShowAllCustomerPreferencesActionConfig
from vocode.streaming.action.sendMail_action import SendContactLogEmailActionConfig,SendContactLogEmailAction
from twilio.rest import *
from pinecone_configs.pincecone_embbeding_router import upload_pdf_router
from websocket_manager import ws_manager

#from outbound_call import make_outbound_call_router
# from in_memory import InMemoryConfigManager
"""Load environment variables"""

from dotenv import load_dotenv
load_dotenv(override=True)

# Constants
BASE_URL = os.getenv("BASE_URL")
elab_key = os.getenv("ELEVEN_LABS_API_KEY")
print (elab_key)
app = FastAPI()
#app.include_router(make_outbound_call_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Initialize RedisConfigManager
config_manager = MongoDBConfigManager(logger=logger)

# Initialize TelephonyServer
telephony_server = TelephonyServer(
    base_url=BASE_URL,
    config_manager=config_manager,
    logger=logger,
)


# Define API routes
@app.get("/")
async def index():
    return {"successful": "Mr Abdul qadoos is checking the site  01...."}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str = Query(...)):
    try:
        # Connect using conversation ID
        await ws_manager.connect(conversation_id, websocket)
        print(f"Client connected: {conversation_id}")

        
        
        
        while True:
            try:
                # Keep the connection alive by waiting for incoming messages or a disconnection
                await websocket.receive_text()  # You can ignore the received text if not needed
            except WebSocketDisconnect:
                print(f"Client disconnected: {conversation_id}")
                await ws_manager.disconnect(conversation_id)
                break
        # while True:
        #     try:
        #         # Send message to the frontend periodically
        #         # await ws_manager.send_message(conversation_id, f"Hello from server to {conversation_id}")
        #         # await asyncio.sleep(5)  # Adjust the interval for sending messages
        #     except WebSocketDisconnect:
        #         print(f"Client disconnected: {conversation_id}")
        #         await ws_manager.disconnect(conversation_id)
        #         break
        #     except Exception as e:
        #         print(f"Error sending message: {e}")
        #         break

    except WebSocketException as e:
        # Handle WebSocket-related exceptions like duplicate conversation IDs
        print(f"Client disconnected: {conversation_id}")
        await ws_manager.disconnect(conversation_id)
        print(f"WebSocket Exception: {e}")

    except Exception as e:
        print(f"Client disconnected: {conversation_id}")
        await ws_manager.disconnect(conversation_id)
        print(f"WebSocket Error: {e}")

    # finally:
    #     # Ensure disconnection happens even on error
    #     await ws_manager.disconnect(conversation_id)
    
    
    
    
    
    
# @app.on_event("startup")
# async def startup_event():
#     print ("start up is running ")
#     await telephony_server.load_configs_from_mongo()
#     app.include_router(telephony_server.get_router())

# Function to match routes
def route_matches(route: APIRoute, name: str) -> bool:
    return route.path == f"/inbound_Call/{name}"


async def remove_route(name: str):
        route_path = f"/inbound_Call/{name}"
    
        # Print routes before removal
        # print("This is app before removal", app.router.routes)
        # print("Telephone router routes before removal", telephony_server.router.routes)
        
        # Find and remove the route from telephony server
        for i, route in enumerate(telephony_server.router.routes):
            if route_matches(route, name):
                del telephony_server.router.routes[i]
                
                # Remove the route from app router
                app.router.routes = [r for r in app.router.routes if r.path != route_path]
                
                # Uncomment if you need to re-include the router
                # app.include_router(telephony_server.get_router())
                print(f"""message: Route from TELEPHONY AND APP removed""")
                return ("NOT Found")
             
        print(f"""message: Route from TELEPHONY AND APP Not Found""")
        return {"message":"Route not found "}




  

# @app.post("/add_inbound_call_config")
# async def add_inbound_call_config(config_request: InboundCallConfigRequest):
#     try:
#         await remove_route(config_request.Agent_id)
        
#         agent_personal_data = await fetch_agent_personal_data(config_request.Agent_id)
#         customer_id = agent_personal_data.customerID
#         print ("hey this is greetings ",agent_personal_data.greetings)
#         agent_keys_data = await fetch_agent_keys_data(customer_id)
        
#         knowledge = await fetch_knowledge_base_data(config_request.Agent_id)
        
#         prompt = generate_prompt(
#             agent_personal_data.AgentName,
#             agent_personal_data.CompanyName,
#             agent_personal_data.CompanyBusiness,
#             agent_personal_data.livetransfer,
#             knowledge
#         )
        
#         new_config = TwilioInboundCallConfig(
#             url=f"/inbound_Call/{config_request.Agent_id}",
#             agent_config=ChatGPTAgentConfig(
#                 temperature=0.6,
#                 model_name="gpt-4o",
#                 allowed_idle_time_seconds=10,
#                 initial_message=BaseMessage(text=agent_personal_data.greetings),
#                 prompt_preamble=prompt,
#                 end_conversation_on_goodbye=True,
#                 generate_responses=False,
#                 allow_agent_to_be_cut_off=True,
#                 openai_api_key=agent_keys_data.openAI,
#                 actions=[TransferCallActionConfig(to_phone=agent_personal_data.livetransfer)]
#             ),
#             transcriber_config=DeepgramTranscriberConfig.from_telephone_input_device(
#                 model="nova-2",
#             ),
#             synthesizer_config=ElevenLabsSynthesizerConfig.from_telephone_output_device(
#                 api_key=agent_keys_data.ElevenLabs,
#                 voice_id=agent_personal_data.audioId,
#                 optimize_streaming_latency=4,
#             ),
#             twilio_config=TwilioConfig(
#                 account_sid=agent_keys_data.accountSID,
#                 auth_token=agent_keys_data.authtoken,
#             ),
#         )
        
#         await telephony_server.mongodb_add_inbound_call_config_1(new_config)
#         app.include_router(telephony_server.get_router())
#         return {"message": "Inbound call config added successfully"}
    
#     except ValidationError as e:
#         raise HTTPException(status_code=422, detail=e.errors())
#     except Exception as e:
#         print ("Errror ",e)
#         raise HTTPException(status_code=400, detail=str(e))

app.include_router(upload_pdf_router)

@app.post("/add_inbound_call_config01")
async def add_inbound_call_config(config_request: InboundCallConfigRequest):
    try:
        await remove_route(config_request.Agent_id)
        print ("i am here ")
        Agent_personal_data = mongo_handler.get_data_from_db_by_obj_ID(collection_name = "agent",object_id =config_request.Agent_id)
        print ("\n\n\n\n\ni am here 1",Agent_personal_data)
        print (Agent_personal_data)
        CustomerId=Agent_personal_data["customerID"]
        print ("CustomerID ",CustomerId)
        print ("\n\n\n\nThis is the ",CustomerId)
        AgentKeysData = mongo_handler.get_data_by_key_and_value("agentkeys","customerID",CustomerId)
        print ("hey how are you ",AgentKeysData)
        
        # Live_url = AgentKeysData["callingserver"]        
        knowledgebaseData = mongo_handler.get_all_data_by_array_value("knowledges","AgentID",config_request.Agent_id )
        print ("knowledgebase  data ",knowledgebaseData)
        # json.dump(knowledgebaseData)
        knowledge=convert_to_string(knowledgebaseData)
        print ("stirng knowledge Base ",knowledge)
        prompt = generate_prompt( Agent_personal_data["AgentName"], Agent_personal_data["CompanyName"], Agent_personal_data["CompanyBusiness"], Agent_personal_data["livetransfer"],knowledge )
        print ("open  ai key ",AgentKeysData["openAI"])
        
        messages = [
        "Okay .",
    "I can't hear you" ]
        
        base_messages = [BaseMessage(text=msg) for msg in messages]
    # Initialize the CutOffResponse object
        cut_off_response = CutOffResponse(messages=base_messages)
        
        
        new_config = TwilioInboundCallConfig(
            url=f"/inbound_Call/{config_request.Agent_id}",
            agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text=Agent_personal_data["greetings"] ),
                temperature=0.6,
                model_name="gpt-4o",
                allowed_idle_time_seconds=20,
                # initial_message=BaseMessage(text="Wellcome to the fabricare services."),
                prompt_preamble=prompt,
                # cut_off_response=[BaseMessage(text="Sorry?"),BaseMessage(text="I cant hear you "),BaseMessage(text="What does that means")],
                end_conversation_on_goodbye=True,
                send_filler_audio=True, 
                allow_agent_to_be_cut_off=True, 
                generate_responses=True,
                openai_api_key=AgentKeysData["openAI"],
                actions=[
                        TransferCallActionConfig(to_phone=Agent_personal_data["livetransfer"]),
                        
                        ExecuteGraphQLQueryByPhoneActionConfig(token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2FwaXRlc3Rpbmcuc21ydGFwcC5jb20iLCJpYXQiOjE3MTk5MTY5NzMsInN1YiI6ImFkbWluIn0.i1-BCUFX4Ac3yPx5Dx8v1eco12L5IV-HajK1kKZlGGo"
,url="https://apitesting.smrtapp.com/graphql"),
                        
                        PutAppointmentActionConfig(token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2FwaXRlc3Rpbmcuc21ydGFwcC5jb20iLCJpYXQiOjE3MTk5MTY5NzMsInN1YiI6ImFkbWluIn0.i1-BCUFX4Ac3yPx5Dx8v1eco12L5IV-HajK1kKZlGGo"
,url="https://apitesting.smrtapp.com/graphql") ,
                        
                        SendContactLogEmailActionConfig(token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2FwaXRlc3Rpbmcuc21ydGFwcC5jb20iLCJpYXQiOjE3MTk5MTY5NzMsInN1YiI6ImFkbWluIn0.i1-BCUFX4Ac3yPx5Dx8v1eco12L5IV-HajK1kKZlGGo"
,url="https://apitesting.smrtapp.com/graphql")                         
                         ]
            ),
            transcriber_config=DeepgramTranscriberConfig.from_telephone_input_device(
                 model="nova-2-phonecall",
                 mute_during_speech=False,
                # chunk_size=4000,
                endpointing_config=PunctuationEndpointingConfig()
            ),
            synthesizer_config=ElevenLabsSynthesizerConfig.from_telephone_output_device(
                api_key=AgentKeysData["ElevenLabs"],
                voice_id= Agent_personal_data["audioId"],
                # voice_id= Agent_personal_data["voice_id"],
                model_id="eleven_turbo_v2",
                optimize_streaming_latency=4,
                experimental_streaming = True,
                stability=0.4,
                similarity_boost=0.8, 
                style=0.15,
                use_speaker_boost=True,
            ),
            twilio_config=TwilioConfig(
                account_sid=AgentKeysData["accountSID"],
                auth_token=AgentKeysData["authtoken"],
            ),
        )
        # new_config
        await telephony_server.mongodb_add_inbound_call_config_1(new_config)
        app.include_router(telephony_server.get_router())
        return {"message": "Inbound call config added successfully"}
    except Exception as e:
        print ("this is the error")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/inbound_call_configs_from_mongo")
async def get_inbound_call_configs():
    return await telephony_server.mongodb_get_all_inbound_call_configs()
    
@app.get ("/Activeroutes")
async def Activeroutes():
    if not telephony_server.inbound_call_configs:
        app.include_router(telephony_server.get_router())    
        raise HTTPException(status_code=404, detail="No inbound call configurations found")
    return {"Inbound_Call_Config":telephony_server.inbound_call_configs}
    
@app.delete("/inbound_call_configs/inbound_Call/{url}")
async def delete_inbound_call_config(url: str):
    try:
        await remove_route(url)
        await telephony_server.mongodb_delete_inbound_call_config(url)
        # Include TelephonyServer router
        app.include_router(telephony_server.get_router())
        return {"message": "Inbound call config deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

from mongodb_config.mongo_db_config import mongo_handler
data = mongo_handler.get_transcription_by_conversation_id("transcription","yyP-Nz13Qdd2nNLxdWDCEQ")
print ("this is transcription ",data)
from outbound_call import make_outbound_call_router
app.include_router(telephony_server.get_router())
app.include_router(make_outbound_call_router)
# Main entry point
account_sid=os.getenv("TWILIO_ACCOUNT_SID")
auth_token=os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)
@app.post('/terminate-this-call')
async def terminate_this_call(data: dict =(...)):
    call_sid = data.get('call_sid')

    try:
        print ("call sid for teminating is : ",call_sid)
        client.calls(call_sid).update(status='completed')
        return {'message': 'Call terminated.'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occured {e}")


@app.post("/status_webhook")
async def twilio_webhook(request: Request):
    # Twilio sends the status updates as form data
    form_data = await request.form()
    ongoing_statuses = ['initiated','ringing', 'answered', 'in-progress']
    final_statuses = ['completed', 'busy', 'failed', 'no-answer', 'canceled']
    # Extract parameters sent by Twilio
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")
    call_duration = form_data.get("CallDuration", "N/A")  # Not always available
    from_number = form_data.get('From')
    to_number = form_data.get('To')
    print (f"Call SID: {call_sid} | Status: {call_status} | Duration: {call_duration}")
    print(f"From: {from_number} | To: {to_number}")
    await ws_manager.send_message(call_sid,f"{call_status}")
    ## Handle ongoing statuses
    #if call_status in ongoing_statuses:
    #    print (f"Ongoing Call Status: {call_status} ")
    #    await ws_manager.send_message("1234567",f" this is the status of the call {call_status}")
    ## Handle final statuses
    #if call_status in final_statuses:
    #    print (f"Final Call Status: {call_status} (Duration: {call_duration},")
    #    await ws_manager.send_message("1234567",f" this is the status of the call {call_status}")
    



@app.post ('/sendwebsocketmessage')
async def sendwebsocketmessage():

   await ws_manager.send_message("1234567","jdasfjasdfa")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.1.0", port=3000)
