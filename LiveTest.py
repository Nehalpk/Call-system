import asyncio
import logging
import signal
from vocode.streaming.streaming_conversation import StreamingConversation
from vocode.helpers import create_streaming_microphone_input_and_speaker_output
from vocode.streaming.transcriber import *
from vocode.streaming.agent import *
from vocode.streaming.synthesizer import *
from vocode.streaming.models.transcriber import *
from vocode.streaming.models.agent import *
from vocode.streaming.models.synthesizer import *
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.message import BaseMessage
import vocode
from dotenv import load_dotenv
import os 
# these can also be set as environment variables
# vocode.setenv(
#     OPENAI_API_KEY="<your OpenAI key>",
#     DEEPGRAM_API_KEY="<your Deepgram key>",
#     AZURE_SPEECH_KEY="<your Azure key>",
#     AZURE_SPEECH_REGION="<your Azure region>",
# )

load_dotenv(override=True)
BASE_URL = os.environ["BASE_URL"]
open_key = os.environ["OPENAI_API_KEY"]
elab_key = os.environ["ELEVEN_LABS_API_KEY"]
print('-----------',elab_key)
origin_phone=os.environ["TWILIO_PHONE_NUMBER"]
TWILIO_ACCOUNT_SID =os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ ["TWILIO_AUTH_TOKEN"]


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

prompt1 = f"""
You are a very abusive voice assistant, You are very rude, sarcastic and you must hurt the other person's feelings. You must strictly use Abusive words as much as you can.
Always use words like "fuck you", "Please Fuck off" and behave like a very rude criminal. Threatning the person.

    """

async def main():
    (
        microphone_input,
        speaker_output,
    ) = create_streaming_microphone_input_and_speaker_output(
        use_default_devices=False,
        logger=logger,
        use_blocking_speaker_output=True
    )

    conversation = StreamingConversation(
        output_device=speaker_output,
        transcriber=DeepgramTranscriber(


            DeepgramTranscriberConfig.from_input_device(
                 microphone_input,
                endpointing_config=PunctuationEndpointingConfig(),
    language="en-us",
    # model = "nova-2-voicemail",
    # detect_language=True,
    # audio_encoding=AudioEncoding.MULAW,
    mute_during_speech=True,
logger=logger
    # tier: Optional[str] = None
    # version: Optional[str] = None
    # keywords: Optional[list] = None
    # endpointing_config=PunctuationEndpointingConfig()
    ),logger=logger
        ),
        agent=ChatGPTAgent(
            ChatGPTAgentConfig(
                initial_message=BaseMessage(text="hey bitch! what the fuck do you want!!!!! "),
    prompt_preamble=prompt1,
    openai_api_key=open_key,
    generate_responses=True,
    model_name="gpt-3.5-turbo-0613",
    temperature=0.2,
    send_filler_audio=True,
    allow_agent_to_be_cut_off=True,
    logger=logger
    # allow_agent_to_be_cut_off=True,
),logger=logger
        ),
        synthesizer= ElevenLabsSynthesizer(ElevenLabsSynthesizerConfig.from_output_device(
        output_device=speaker_output,
        model_id="eleven_turbo_v2",
        # api_key=elab_key,
        voice_id ="EGQM7bHbTHTb7VUEcOHG",
        # optimize_streaming_latency=4,
        # experimental_streaming = True,
        # stability=0.8,
        # similarity_boost=0.2,
        # audio_encoding="mulaw"
        logger=logger
        ),
        logger=logger,
        ))
    await conversation.start()
    print("Conversation started, press Ctrl+C to end")
    signal.signal(
        signal.SIGINT, lambda _0, _1: asyncio.create_task(conversation.terminate())
    )
    while conversation.is_active():
        chunk = await microphone_input.get_audio()
        conversation.receive_audio(chunk)


if __name__ == "__main__":
    asyncio.run(main())