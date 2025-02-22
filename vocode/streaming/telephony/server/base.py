
import abc
from functools import partial
import logging
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig
from typing import List, Optional
from fastapi import APIRouter, Form, Request, Response
from pydantic import BaseModel, Field
from vocode.streaming.agent.factory import AgentFactory
from vocode.streaming.models.agent import AgentConfig
from vocode.streaming.models.events import RecordingEvent
from vocode.streaming.models.synthesizer import SynthesizerConfig
from vocode.streaming.models.transcriber import TranscriberConfig
from vocode.streaming.synthesizer.factory import SynthesizerFactory
from vocode.streaming.telephony.client.base_telephony_client import BaseTelephonyClient
from vocode.streaming.telephony.client.twilio_client import TwilioClient
from vocode.streaming.telephony.client.vonage_client import VonageClient
from vocode.streaming.telephony.config_manager.base_config_manager import BaseConfigManager
from vocode.streaming.telephony.constants import DEFAULT_AUDIO_ENCODING, DEFAULT_CHUNK_SIZE, DEFAULT_SAMPLING_RATE, VONAGE_AUDIO_ENCODING, VONAGE_SAMPLING_RATE
from vocode.streaming.telephony.server.router.calls import CallsRouter
from vocode.streaming.models.telephony import TwilioCallConfig, TwilioConfig, VonageCallConfig, VonageConfig
from vocode.streaming.telephony.templater import Templater
from vocode.streaming.transcriber.base_transcriber import BaseTranscriber
from vocode.streaming.transcriber.factory import TranscriberFactory
from vocode.streaming.utils import create_conversation_id
from vocode.streaming.utils.events_manager import EventsManager
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Union
import os 
# MongoDB settings
MONGO_DB_URL = "mongodb+srv://maaz0301301:5uI9SlSVLIGOzTgo@cluster0.prqfiyx.mongodb.net/"
MONGO_DB_NAME = "fabi-careDB"
COLLECTION_NAME = "inbound_call_configs"

class AbstractInboundCallConfig(BaseModel, abc.ABC):
    url: str
    agent_config: AgentConfig
    transcriber_config: Optional[TranscriberConfig] = None
    synthesizer_config: Optional[SynthesizerConfig] = None

class TwilioInboundCallConfig(AbstractInboundCallConfig):
    twilio_config: TwilioConfig

class VonageInboundCallConfig(AbstractInboundCallConfig):
    vonage_config: VonageConfig

class VonageAnswerRequest(BaseModel):
    to: str
    from_: str = Field(..., alias="from")
    uuid: str

class TelephonyServer:
    def __init__(self, base_url: str, config_manager: BaseConfigManager, inbound_call_configs: List[AbstractInboundCallConfig] = [], transcriber_factory: TranscriberFactory = TranscriberFactory(), agent_factory: AgentFactory = AgentFactory(), synthesizer_factory: SynthesizerFactory = SynthesizerFactory(), events_manager: Optional[EventsManager] = None, logger: Optional[logging.Logger] = None):
        self.base_url = base_url
        self.logger = logger or logging.getLogger(__name__)
        self.router = APIRouter()
        self.config_manager = config_manager
        self.templater = Templater()
        self.events_manager = events_manager
        self.inbound_call_configs = inbound_call_configs
        self.router.include_router(
            CallsRouter(
                base_url=base_url,
                config_manager=self.config_manager,
                transcriber_factory=transcriber_factory,
                agent_factory=agent_factory,
                synthesizer_factory=synthesizer_factory,
                events_manager=self.events_manager,
                logger=self.logger,
            ).get_router()
        )
        for config in inbound_call_configs:
            self.router.add_api_route(
                config.url,
                self.create_inbound_route(inbound_call_config=config),
                methods=["POST"],
            )
        self.router.add_api_route("/events", self.events, methods=["GET", "POST"])
        self.logger.info(f"Set up events endpoint at https://{self.base_url}/events")

        self.router.add_api_route("/recordings/{conversation_id}", self.recordings, methods=["GET", "POST"])
        self.logger.info(f"Set up recordings endpoint at https://{self.base_url}/recordings/{{conversation_id}}")

        # MongoDB client setup
        self.mongo_client = AsyncIOMotorClient(MONGO_DB_URL)
        self.mongo_db = self.mongo_client[MONGO_DB_NAME]
        self.mongo_collection = self.mongo_db[COLLECTION_NAME]

    def events(self, request: Request):
        return Response()

    async def recordings(self, request: Request, conversation_id: str):
        recording_url = (await request.json())["recording_url"]
        if self.events_manager is not None and recording_url is not None:
            self.events_manager.publish_event(RecordingEvent(recording_url=recording_url, conversation_id=conversation_id))
        return Response()

    def create_inbound_route(self, inbound_call_config: AbstractInboundCallConfig):
        async def twilio_route(twilio_config: TwilioConfig, twilio_sid: str = Form(alias="CallSid"), twilio_from: str = Form(alias="From"), twilio_to: str = Form(alias="To")) -> Response:
            call_config = TwilioCallConfig(
                transcriber_config=inbound_call_config.transcriber_config or TwilioCallConfig.default_transcriber_config(),
                agent_config=inbound_call_config.agent_config,
                synthesizer_config=inbound_call_config.synthesizer_config or TwilioCallConfig.default_synthesizer_config(),
                twilio_config=twilio_config,
                twilio_sid=twilio_sid,
                from_phone=twilio_from,
                to_phone=twilio_to,
            )
            conversation_id = create_conversation_id()
            await self.config_manager.save_config(conversation_id, call_config)
            return self.templater.get_connection_twiml(base_url=self.base_url, call_id=conversation_id)

        async def vonage_route(vonage_config: VonageConfig, vonage_answer_request: VonageAnswerRequest):
            call_config = VonageCallConfig(
                transcriber_config=inbound_call_config.transcriber_config or VonageCallConfig.default_transcriber_config(),
                agent_config=inbound_call_config.agent_config,
                synthesizer_config=inbound_call_config.synthesizer_config or VonageCallConfig.default_synthesizer_config(),
                vonage_config=vonage_config,
                vonage_uuid=vonage_answer_request.uuid,
                to_phone=vonage_answer_request.from_,
                from_phone=vonage_answer_request.to,
            )
            conversation_id = create_conversation_id()
            await self.config_manager.save_config(conversation_id, call_config)
            return VonageClient.create_call_ncco(base_url=self.base_url, conversation_id=conversation_id, record=vonage_config.record)

        if isinstance(inbound_call_config, TwilioInboundCallConfig):
            self.logger.info(f"Set up inbound call TwiML at https://{self.base_url}{inbound_call_config.url}")
            return partial(twilio_route, inbound_call_config.twilio_config)
        elif isinstance(inbound_call_config, VonageInboundCallConfig):
            self.logger.info(f"Set up inbound call NCCO at https://{self.base_url}{inbound_call_config.url}")
            return partial(vonage_route, inbound_call_config.vonage_config)
        else:
            raise ValueError(f"Unknown inbound call config type {type(inbound_call_config)}")

    async def end_outbound_call(self, conversation_id: str):
        call_config = await self.config_manager.get_config(conversation_id)
        if not call_config:
            raise ValueError(f"Could not find call config for {conversation_id}")
        telephony_client: BaseTelephonyClient
        if isinstance(call_config, TwilioCallConfig):
            telephony_client = TwilioClient(base_url=self.base_url, twilio_config=call_config.twilio_config)
            await telephony_client.end_call(call_config.twilio_sid)
        elif isinstance(call_config, VonageCallConfig):
            telephony_client = VonageClient(base_url=self.base_url, vonage_config=call_config.vonage_config)
            await telephony_client.end_call(call_config.vonage_uuid)
        return {"id": conversation_id}
    
    async def add_inbound_call_config(self, new_config: AbstractInboundCallConfig):
        try:
            # Check if the configuration already exists
            if any(config.url == new_config.url for config in self.inbound_call_configs):
                raise ValueError(f"Configuration with URL {new_config.url} already exists")
            
            self.inbound_call_configs.append(new_config)
            self.router.add_api_route(new_config.url, self.create_inbound_route(inbound_call_config=new_config), methods=["POST"])
            self.logger.info(f"Added new inbound call configuration at {new_config.url}")
        except ValueError as ve:
            self.logger.warning(ve)
            raise
        except Exception as e:
            self.logger.error(f"Failed to add new inbound call configuration at {new_config.url}: {e}")
            raise

    def get_inbound_call_config(self, url: str) -> Optional[AbstractInboundCallConfig]:
        try:
            url = f'/{url}'
            for config in self.inbound_call_configs:
                if config.url == url:
                    return config
            return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve inbound call configuration for {url}: {e}")
            raise

    
    def update_inbound_call_config(self, url: str, updated_config: AbstractInboundCallConfig):
        try:
            url = f'/{url}'
            for i, config in enumerate(self.inbound_call_configs):
                if config.url == url:
                    self.inbound_call_configs[i] = updated_config
                    self.router.routes = [route for route in self.router.routes if not (route.path == config.url and "POST" in route.methods)]
                    self.router.add_api_route(updated_config.url, self.create_inbound_route(inbound_call_config=updated_config), methods=["POST"])
                    self.logger.info(f"Updated inbound call configuration at {url}")
                    return
            raise ValueError(f"Configuration with URL {url} not found")
        except ValueError as ve:
            self.logger.warning(ve)
            raise
        except Exception as e:
            self.logger.error(f"Failed to update inbound call configuration at {url}: {e}")
            raise

   
    async def delete_inbound_call_config(self, url: str):
        try:
            url = f'{url}'
            
            # Check if the configuration exists
            if not any(config.url == url for config in self.inbound_call_configs):
                raise ValueError(f"No configuration found for URL {url}")

            # Delete the configuration
            self.inbound_call_configs = [config for config in self.inbound_call_configs if config.url != url]
            self.router.routes = [route for route in self.router.routes if not (route.path == url and "POST" in route.methods)]
            self.logger.info(f"Deleted inbound call configuration at {url}")
            
        except ValueError as ve:
            self.logger.warning(ve)
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete inbound call configuration at {url}: {e}")
            raise

    async def mongodb_add_inbound_call_config(self, new_config: AbstractInboundCallConfig):
        try:
            print(new_config)
            existing_config = await self.mongo_collection.find_one({"url": new_config.url})
            if existing_config:
                raise ValueError(f"Configuration with URL {new_config.url} already exists")

            # Insert the new configuration into MongoDB
            await self.mongo_collection.insert_one(new_config.dict())
            self.inbound_call_configs.append(new_config)
            self.router.add_api_route(new_config.url, self.create_inbound_route(inbound_call_config=new_config), methods=["POST"])
            self.logger.info(f"Added new inbound call configuration at {new_config.url}")
        except ValueError as ve:
            self.logger.warning(ve)
            raise
        except Exception as e:
            self.logger.error(f"Failed to add new inbound call configuration at {new_config.url}: {e}")
            raise

    async def mongodb_add_inbound_call_config_1(self, new_config: AbstractInboundCallConfig):
        try:
            # print(new_config)
            existing_config = await self.mongo_collection.find_one({"url": new_config.url})
            if existing_config:
                # Delete the existing configuration
                await self.mongo_collection.delete_one({"url": new_config.url})
                self.inbound_call_configs = [config for config in self.inbound_call_configs if config.url != new_config.url]
                # self.router.routes = [route for route in self.router.routes if not (route.path == new_config.url and "POST" in route.methods)]
                self.logger.info(f"Deleted existing inbound call configuration at {new_config.url}")

            # Insert the new configuration into MongoDB
            await self.mongo_collection.insert_one(new_config.dict())
            self.inbound_call_configs.append(new_config)
            self.router.add_api_route(new_config.url, self.create_inbound_route(inbound_call_config=new_config), methods=["POST"])
            self.logger.info(f"Added new inbound call configuration at {new_config.url}")
        except Exception as e:
            self.logger.error(f"Failed to add new inbound call configuration at {new_config.url}: {e}")
            raise

    async def fetch_config_by_url(self, url: str) -> Optional[TwilioInboundCallConfig]:
        try:
            config_request = await self.mongo_collection.find_one({"url": f"/{url}"})
            if config_request:
                config_request.pop('_id', None)  # Remove the _id field from the dictionary
                config_data = TwilioInboundCallConfig(
                                url=config_request["url"],
                                agent_config=ChatGPTAgentConfig(
                                    initial_message=BaseMessage(**config_request["agent_config"]["initial_message"]),
                                    prompt_preamble=config_request["agent_config"]["prompt_preamble"],
                                    end_conversation_on_goodbye=config_request["agent_config"]["end_conversation_on_goodbye"],
                                    generate_responses=config_request["agent_config"]["generate_responses"],
                                    model_name=config_request["agent_config"]["model_name"],
                                    temperature=config_request["agent_config"]["temperature"],
                                    max_tokens=config_request["agent_config"]["max_tokens"],
                                    # Map the remaining fields as necessary
                                ),
                                transcriber_config=DeepgramTranscriberConfig(
                                    model=config_request["transcriber_config"]["model"],
                                    sampling_rate=config_request["transcriber_config"]["sampling_rate"],
                                    audio_encoding=config_request["transcriber_config"]["audio_encoding"],
                                    chunk_size=config_request["transcriber_config"]["chunk_size"],
                                    # Map the remaining fields as necessary
                                ),
                                synthesizer_config=ElevenLabsSynthesizerConfig(
                                    api_key=config_request["synthesizer_config"]["api_key"],
                                    voice_id=config_request["synthesizer_config"]["voice_id"],
                                    optimize_streaming_latency=config_request["synthesizer_config"]["optimize_streaming_latency"],
                                    sampling_rate=config_request["synthesizer_config"]["sampling_rate"],
                                    audio_encoding=config_request["synthesizer_config"]["audio_encoding"],
                                    should_encode_as_wav=config_request["synthesizer_config"]["should_encode_as_wav"],
                                    experimental_streaming=config_request["synthesizer_config"]["experimental_streaming"],
                                    # Map the remaining fields as necessary
                                ),
                                twilio_config=TwilioConfig(
                                    account_sid=config_request["twilio_config"]["account_sid"],
                                    auth_token=config_request["twilio_config"]["auth_token"],
                                    record=config_request["twilio_config"]["record"],
                                    extra_params=config_request["twilio_config"]["extra_params"],
                                    # Map the remaining fields as necessary
                                )
                            )

                return config_data
            else:
                self.logger.info(f"No configuration found for URL: {url}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to fetch configuration for URL {url}: {e}")
            raise
    async def mongodb_get_all_inbound_call_configs(self) -> Union[List[AbstractInboundCallConfig], List[dict]]:
        try:
            configs = []
            async for document in self.mongo_collection.find():
                if 'twilio_config' in document:
                    configs.append(TwilioInboundCallConfig(**document))
                elif 'vonage_config' in document:
                    configs.append(VonageInboundCallConfig(**document))
                else:
                    configs.append(document)
            return configs
        except Exception as e:
            self.logger.error(f"Failed to retrieve inbound call configurations: {e}")
            raise

    async def mongodb_get_inbound_call_config(self, url: str) -> AbstractInboundCallConfig:
        try:
            config_request = await self.mongo_collection.find_one({"url": f"/{url}"})
            if config_request:
                config_request.pop('_id', None)  # Remove the _id field from the dictionary
                config_data = TwilioInboundCallConfig(
                                url=config_request["url"],
                                agent_config=ChatGPTAgentConfig(
                                    initial_message=BaseMessage(**config_request["agent_config"]["initial_message"]),
                                    prompt_preamble=config_request["agent_config"]["prompt_preamble"],
                                    end_conversation_on_goodbye=config_request["agent_config"]["end_conversation_on_goodbye"],
                                    generate_responses=config_request["agent_config"]["generate_responses"],
                                    model_name=config_request["agent_config"]["model_name"],
                                    temperature=config_request["agent_config"]["temperature"],
                                    max_tokens=config_request["agent_config"]["max_tokens"],
                                    # Map the remaining fields as necessary
                                ),
                                transcriber_config=DeepgramTranscriberConfig(
                                    model=config_request["transcriber_config"]["model"],
                                    sampling_rate=config_request["transcriber_config"]["sampling_rate"],
                                    audio_encoding=config_request["transcriber_config"]["audio_encoding"],
                                    chunk_size=config_request["transcriber_config"]["chunk_size"],
                                    # Map the remaining fields as necessary
                                ),
                                synthesizer_config=ElevenLabsSynthesizerConfig(
                                    api_key=config_request["synthesizer_config"]["api_key"],
                                    voice_id=config_request["synthesizer_config"]["voice_id"],
                                    optimize_streaming_latency=config_request["synthesizer_config"]["optimize_streaming_latency"],
                                    sampling_rate=config_request["synthesizer_config"]["sampling_rate"],
                                    audio_encoding=config_request["synthesizer_config"]["audio_encoding"],
                                    should_encode_as_wav=config_request["synthesizer_config"]["should_encode_as_wav"],
                                    experimental_streaming=config_request["synthesizer_config"]["experimental_streaming"],
                                    # Map the remaining fields as necessary
                                ),
                                twilio_config=TwilioConfig(
                                    account_sid=config_request["twilio_config"]["account_sid"],
                                    auth_token=config_request["twilio_config"]["auth_token"],
                                    record=config_request["twilio_config"]["record"],
                                    extra_params=config_request["twilio_config"]["extra_params"],
                                    # Map the remaining fields as necessary
                                )
                            )

                return config_data
            else:
                self.logger.info(f"No configuration found for URL: {url}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve configuration for URL {url}: {e}")
            raise
    # async def mongodb_get_inbound_call_config(self, url: str) -> Optional[AbstractInboundCallConfig]:
        # try:
        #     document = await self.mongo_collection.find_one({"url": f"/{url}"})
        #     if document:
        #         if 'twilio_config' in document:
        #             return TwilioInboundCallConfig(**document)
        #         elif 'vonage_config' in document:
        #             return VonageInboundCallConfig(**document)
        #     return None
        # except Exception as e:
        #     self.logger.error(f"Failed to retrieve inbound call configuration for {url}: {e}")
        #     raise
            
    async def mongodb_update_inbound_call_config(self, url: str, updated_config: AbstractInboundCallConfig):
        try:
            result = await self.mongo_collection.update_one(
                {"url": f"/{url}"},
                {"$set": updated_config.dict()}
            )
            if result.matched_count:
                for i, config in enumerate(self.inbound_call_configs):
                    if config.url == url:
                        self.inbound_call_configs[i] = updated_config
                        self.router.routes = [route for route in self.router.routes if not (route.path == config.url and "POST" in route.methods)]
                        self.router.add_api_route(updated_config.url, self.create_inbound_route(inbound_call_config=updated_config), methods=["POST"])
                        self.logger.info(f"Updated inbound call configuration at {url}")
                        return
            else:
                raise ValueError(f"Configuration with URL /{url} not found")
        except ValueError as ve:
            self.logger.warning(ve)
            raise
        except Exception as e:
            self.logger.error(f"Failed to update inbound call configuration at /{url}: {e}")
            raise

    async def mongodb_delete_inbound_call_config(self, url: str):
        try:
            url1 =f"/inbound_Call/{url}"
            print ("this is url for deletion ",url1)
            await self.delete_inbound_call_config(url1)
            result = await self.mongo_collection.delete_one({"url":url1 })
            if result.deleted_count:
                self.inbound_call_configs = [config for config in self.inbound_call_configs if config.url != url]
                self.router.routes = [route for route in self.router.routes if not (route.path == url and "POST" in route.methods)]
                self.logger.info(f"Deleted inbound call configuration at {url}")
            else:
                raise ValueError(f"No configuration found for URL {url}")
        except ValueError as ve:
            self.logger.warning(ve)
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete inbound call configuration at {url}: {e}")
            raise
    
    
    async def load_configs_from_mongo(self):
        
        try:
            print ("Hi there ")
            # Retrieve all configurations from MongoDB
            async for config_request in self.mongo_collection.find():
                print ("Hi there ")
                # Determine the configuration type
                if config_request:
                    config_request.pop('_id', None)  # Remove the _id field from the dictionary
                    config_data = TwilioInboundCallConfig(
                                    url=config_request["url"],
                                    agent_config=ChatGPTAgentConfig(
                                        initial_message=BaseMessage(**config_request["agent_config"]["initial_message"]),
                                        prompt_preamble=config_request["agent_config"]["prompt_preamble"],
                                        end_conversation_on_goodbye=config_request["agent_config"]["end_conversation_on_goodbye"],
                                        generate_responses=config_request["agent_config"]["generate_responses"],
                                        model_name=config_request["agent_config"]["model_name"],
                                        temperature=config_request["agent_config"]["temperature"],
                                        max_tokens=config_request["agent_config"]["max_tokens"],
                                        openai_api_key=config_request["agent_config"]["openai_api_key"]
                                        # Map the remaining fields as necessary
                                    ),
                                    transcriber_config=DeepgramTranscriberConfig(
                                        model=config_request["transcriber_config"]["model"],
                                        sampling_rate=config_request["transcriber_config"]["sampling_rate"],
                                        audio_encoding=config_request["transcriber_config"]["audio_encoding"],
                                        chunk_size=config_request["transcriber_config"]["chunk_size"],
                                        # Map the remaining fields as necessary
                                    ),
                                    synthesizer_config=ElevenLabsSynthesizerConfig(
                                        api_key=config_request["synthesizer_config"]["api_key"],
                                        voice_id=config_request["synthesizer_config"]["voice_id"],
                                        optimize_streaming_latency=config_request["synthesizer_config"]["optimize_streaming_latency"],
                                        sampling_rate=config_request["synthesizer_config"]["sampling_rate"],
                                        audio_encoding=config_request["synthesizer_config"]["audio_encoding"],
                                        should_encode_as_wav=config_request["synthesizer_config"]["should_encode_as_wav"],
                                        experimental_streaming=config_request["synthesizer_config"]["experimental_streaming"],
                                        # Map the remaining fields as necessary
                                    ),
                                    twilio_config=TwilioConfig(
                                        account_sid=config_request["twilio_config"]["account_sid"],
                                        auth_token=config_request["twilio_config"]["auth_token"],
                                        record=config_request["twilio_config"]["record"],
                                        extra_params=config_request["twilio_config"]["extra_params"],
                                        # Map the remaining fields as necessary
                                    )
                                )

                    # if not any(config.url == config_data.url for config in self.inbound_call_configs):
                    #     # Add the new configuration to inbound_call_configs
                    #     self.inbound_call_configs.append(config_data)
                    #     # Set up the corresponding API route
                    #     self.router.add_api_route(config_data.url, self.create_inbound_route(inbound_call_config=config_data), methods=["POST"])
                    #     self.logger.info(f"Added inbound call configuration from MongoDB at {config_data.url}")
                    await self.add_inbound_call_config(config_data)
                # else:
                #     self.logger.info(f"No configuration found")
                #     return None
                # Check if the configuration already exists in inbound_call_configs
                
        except Exception as e:
            self.logger.error(f"Failed to synchronize inbound call configurations with MongoDB: {e}")
            raise
            
    def get_router(self) -> APIRouter:
        return self.router



