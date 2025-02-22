import os
import re
from dotenv import load_dotenv
from vocode.streaming.action.transfer_call import  TransferCallActionConfig
from vocode.streaming.action.nylas_send_email import NylasSendEmailActionConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.telephony.conversation.outbound_call import OutboundCall
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig, PunctuationEndpointingConfig
from vocode.streaming.models.audio_encoding import AudioEncoding
from vocode.streaming.telephony.config_manager.redis_config_manager import (
    RedisConfigManager,)
from vocode.streaming.telephony.config_manager.base_config_manager import (
    BaseConfigManager,
)
from vocode.streaming.action.knowledgebasefetcher import QueryActionConfig
from vocode.streaming.models.vector_db import PineconeConfig 
from fastapi import APIRouter, HTTPException
from mongo_config_manager import MongoDBConfigManager
from vocode.streaming.models.telephony import TwilioConfig
from pydantic import BaseModel,validator
from mongodb_config.mongo_db_config import mongo_handler
from Pydantics_base_configs.add_inbound_config_pydantic import *
from Utilitiess.prompt import generate_prompt
from mongodb_config.mongo_db_config import mongo_handler
import asyncio
# from in_memory import InMemoryConfigManager
load_dotenv(override=True)
BASE_URL = os.environ["BASE_URL"]
# Twilio_Number = os.environ["TWILIO_PHONE_NUMBER"]
Eleven_lab_APi= os.environ["ELEVEN_LABS_API_KEY"]
TWILIO_ACCOUNT_SID=os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN= os.environ["TWILIO_AUTH_TOKEN"]
OPENAI_API_KEY= os.environ["OPENAI_API_KEY"]
class OuboundCallConfigs(BaseModel):
    Agent_id: str 
    number_to_call: str

    @validator('number_to_call')
    def validate_phone_number(cls, v):
        # This regex pattern allows for various international formats
        pattern = r'^\+?1?\d{9,15}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid phone number format')
        return v

async def make_outbound_call(config_request: OuboundCallConfigs):
    try:
        # Validate phone number
        if not config_request.number_to_call:
            raise ValueError("Phone number is empty")

        print(mongo_handler.ensure_collection("agents"))
        agent_personal_data = mongo_handler.get_data_from_db_by_obj_ID(collection_name="agents", object_id=config_request.Agent_id) 
        print("this is the data", agent_personal_data)
        
        AgentName = agent_personal_data['AgentName']
        FallBackNote = agent_personal_data['FallBackNote']
        audioId = agent_personal_data['audioId']
        CompanyName = agent_personal_data['CompanyName']
        greetings = agent_personal_data['greetings']
        customerID = agent_personal_data['customerID']
        #Audience = agent_personal_data['Audience']
        Maximum_Tokens = agent_personal_data['Maximum_Tokens']
        Temperature = agent_personal_data['Temperature']
        prompt_from_db = agent_personal_data['Script']
        Model = agent_personal_data['Model']
        Twilio_Number=agent_personal_data['phoneNumber']
        knowledgebase_index_name = agent_personal_data['knowledgeBaseId']





        print(f"""The Agent details are: 
               AgentName={AgentName}
               FallBackNote={FallBackNote}
               audioId={audioId}
               CompanyName={CompanyName}
               greetings={greetings}
               customerID={customerID}
               Maximum_Tokens={Maximum_Tokens}
               Temperature={Temperature}
                Model={Model}
                prompt_from_db={prompt_from_db}
                indexname = {knowledgebase_index_name}
               """)
        
        prompt = generate_prompt(AgentName, CompanyName)
        
        # ElevenLab Synthesizer  
        ElevenLab_SYNTH_CONFIG = ElevenLabsSynthesizerConfig.from_telephone_output_device(
            api_key="sk_cdb9e3a9f987ad6f2f9f2d4e27adc8ecf86d2e128ebd4731",
            voice_id=audioId,
            model_id="eleven_turbo_v2",
            optimize_streaming_latency=4,
            experimental_streaming=True,
            stability=0.6,
            similarity_boost=0.65, 
            style=0.15,
            use_speaker_boost=True,
        )

        # TRANSCRIBER CONFIGURATION 
        Deepgram_TRANS_CONFIG = DeepgramTranscriberConfig.from_telephone_input_device(
            language="en-US",
            model="nova-2-phonecall",
            mute_during_speech=False,
        )
        
        AGENT_CONFIG = ChatGPTAgentConfig(
            initial_message=BaseMessage(text=f"{greetings}"),
            prompt_preamble=prompt_from_db,
            model_name='gpt-4o',
            openai_api_key=OPENAI_API_KEY,
            generate_responses=True,
            end_conversation_on_goodbye=True,
            send_filler_audio=True,
            temperature=Temperature,
            allow_agent_to_be_cut_off=True,
            # ,KnowledgebaseActionConfig(index_name = "66ee62824e560426c2514dae",open_ai_key=OPENAI_API_KEY)
            actions=[TransferCallActionConfig(to_phone="+923185127674"),QueryActionConfig(index_name = knowledgebase_index_name,url="https://ai-lead-generation-nodejs.onrender.com/pinecone/query")],
            # vector_db_config= PineconeConfig(
            #                 # index=knowledgebase_index_name,
            #                 index="66ee62824e560426c2514dae",     # Provide the specific index name for Pinecone
            #                 api_key=os.environ["PINECONE_API_KEY"],  # Op,tionally provide the API key
            #                 # api_environment="your_environment",  # Optionally provide the API environment
            #                 top_k=3                        # You can adjust top_k based on your needs
            #             )

        )

        config_manager = MongoDBConfigManager()
        outbound_call = OutboundCall(
            base_url=BASE_URL,
            to_phone=config_request.number_to_call,
            from_phone=Twilio_Number,
            config_manager=config_manager,
            agent_config=AGENT_CONFIG, 
            synthesizer_config=ElevenLab_SYNTH_CONFIG,
            transcriber_config=Deepgram_TRANS_CONFIG,
            status_callback1="https://appto.xya-tech.info/status_webhook",
            status_callback_event1 =['completed', 'busy', 'failed', 'no-answer', 'canceled','queued', 'initiated', 'ringing', 'answered', 'in-progress'],
            #status_callback1="https://f945-2407-d000-1a-fe4b-5928-40f3-a587-76e5.ngrok-free.app/status_webhook",
            #status_callback_event1 =['completed', 'busy', 'failed', 'no-answer', 'canceled','queued', 'initiated', 'ringing', 'answered', 'in-progress'],
            twilio_config=TwilioConfig(
                account_sid=TWILIO_ACCOUNT_SID,
                auth_token=TWILIO_AUTH_TOKEN,
                record=True,        
            ),
        ) 

        # Set a timeout for the call attempt
        try:
            await asyncio.wait_for(outbound_call.start(), timeout=30.0)  # 30 seconds timeout
        except asyncio.TimeoutError:
            raise Exception("Call attempt timed out")

        return outbound_call.telephony_id, outbound_call.conversation_id

    except ValueError as ve:
        # Catch specific ValueError for phone number validation
        print(f"Phone number validation error: {str(ve)}")
        raise Exception(f"Invalid phone number: {str(ve)}")
    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error in make_outbound_call: {str(e)}")
        # Raise an exception that can be caught by the route handler
        raise Exception(f"Failed to make outbound call: {str(e)}")

from fastapi import APIRouter
make_outbound_call_router = APIRouter()
@make_outbound_call_router.post("/make_outbound_call_route")
async def make_outbound_call_route(config_request: OuboundCallConfigs):
    try:
        telephony_id, conversation_id = await make_outbound_call(config_request)
        return {"status": "success", "telephony_id": telephony_id, "conversation_id": conversation_id}
    except Exception as e:
        if "Invalid phone number" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=str(e))