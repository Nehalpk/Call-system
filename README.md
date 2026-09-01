<<<<<<< HEAD
First make virtual env 
Then make sure python version should be 10.0 
run command in virtual env poetry install 
and then poetry run uvicorn main:app --port 8000 
enjoy the code :~
=======
# Call-system
Call  system
>>>>>>> b5c63959272f7c10285e8785c14e5a6737f28b7f
# AI Call System

A real-time AI-powered voice-agent and telephony backend built with Python and FastAPI.

The project provides infrastructure for creating configurable conversational AI agents that can handle inbound and outbound telephone calls, interact with users in real time, retrieve knowledge, execute external actions, and connect with third-party business systems.

The system combines telephony, speech recognition, speech synthesis, large language models, persistent agent configuration, vector-based knowledge retrieval, WebSocket communication, and external API actions into a single backend.

## Overview

The Call System was designed as a configurable backend for AI voice agents rather than as a single hard-coded chatbot.

Each agent can have its own:

- name and identity
- company information
- greeting
- system prompt
- language-model configuration
- temperature and response behaviour
- voice configuration
- knowledge base
- telephone number
- live-transfer number
- external actions
- customer configuration

Agent information can be stored and retrieved from MongoDB and used to dynamically configure the conversational pipeline.

The backend supports both inbound and outbound calling workflows.

## Core Architecture

A typical conversation follows this flow:

```text
Telephone User
      |
      v
Twilio Telephony
      |
      v
Streaming Audio
      |
      v
Deepgram Speech-to-Text
      |
      v
AI Voice Agent / LLM
      |
      +--------------------+
      |                    |
      v                    v
Knowledge Retrieval    External Actions
 / Pinecone              / APIs
      |                    |
      +---------+----------+
                |
                v
        Generated Response
                |
                v
        ElevenLabs TTS
                |
                v
          Twilio Audio
                |
                v
             Caller
```

FastAPI provides the main service and API layer, while MongoDB is used for storing agent configuration and conversation-related information.

## Main Features

### 1. AI Voice Agents

The backend supports configurable conversational AI agents using GPT-based language models.

Agent configuration can include:

- initial greeting
- prompt / behavioural instructions
- model selection
- temperature
- idle-time behaviour
- interruption handling
- conversation-ending logic
- live-call transfer
- external actions
- knowledge-base access

This allows multiple agents to operate with different personalities, businesses, prompts, and workflows.

### 2. Inbound Call Handling

Inbound call configurations can be dynamically created for different agents.

The system can:

- load agent configuration from MongoDB
- create an inbound call route
- connect the telephone stream to the AI agent
- initialize speech recognition
- initialize speech synthesis
- provide the agent with customer-specific instructions
- execute external actions during the call

Dynamic routing means different AI agents can be associated with different call configurations without maintaining a separate backend for every agent.

### 3. Outbound Calling

The project also contains an outbound calling workflow.

The outbound pipeline can:

- validate telephone numbers
- retrieve agent configuration
- initialize the conversational agent
- configure speech-to-text and text-to-speech services
- start an outbound Twilio call
- track call and conversation identifiers
- receive call-status callbacks
- enable call recording
- return telephony and conversation IDs to the calling application

This can support use cases such as:

- customer follow-up
- appointment reminders
- lead qualification
- service calls
- automated business communication

### 4. Real-Time Speech Recognition

Deepgram is used as part of the streaming transcription pipeline.

The implementation includes telephone-oriented transcription configuration and support for phone-call speech models.

The transcribed user speech is passed to the conversational agent for response generation.

### 5. Real-Time Speech Synthesis

ElevenLabs is integrated for speech synthesis.

Voice configuration can include:

- selected voice
- streaming behaviour
- latency optimization
- stability
- similarity settings
- voice style
- speaker-boost settings

This allows the conversational agent to return synthesized speech during an active telephone conversation.

### 6. Large Language Model Integration

The conversational layer uses GPT-based agents.

The system allows model behaviour to be customized using:

- prompt instructions
- greetings
- knowledge
- company information
- temperature
- maximum-token settings
- external actions

The goal is to allow the same infrastructure to support multiple use cases without hard-coding a single dialogue flow.

### 7. Knowledge Base and Retrieval

The repository contains Pinecone and document-processing components for retrieval-oriented agent knowledge.

The knowledge workflow includes functionality for:

- document ingestion
- PDF processing
- text extraction
- document chunking
- embedding text
- storing vectors in Pinecone
- querying agent-specific knowledge

This enables an agent to use external business or domain information rather than relying only on the underlying language model.

Potential knowledge sources can include:

- company FAQs
- product information
- service information
- customer-support material
- policy documents
- business documentation

### 8. External Agent Actions

The conversational agent is designed to perform actions rather than only generate text.

The repository includes integrations or configuration for actions such as:

- live-call transfer
- GraphQL queries
- appointment creation
- customer-preference lookup
- customer-preference updates
- sending contact-log emails
- knowledge-base querying

This provides a foundation for tool-using or agentic workflows where the language model can interact with external systems.

### 9. WebSocket Communication

FastAPI WebSockets are used for real-time communication associated with conversations.

WebSocket connections can be linked to conversation IDs, allowing external clients or frontends to receive information associated with a running conversation.

This can be useful for:

- live dashboards
- real-time transcripts
- call monitoring
- agent status
- conversation state
- frontend notifications

### 10. Persistent Agent Configuration

MongoDB is used to store configuration required by the call system.

The backend can retrieve information such as:

- agent configuration
- customer configuration
- model settings
- voice settings
- greetings
- prompts
- knowledge-base identifiers
- telephone configuration

This separates runtime configuration from the core application code.

## Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- WebSockets

### AI / LLM

- OpenAI
- GPT-based conversational agents
- LangChain components

### Voice and Telephony

- Twilio
- Vocode
- Deepgram
- ElevenLabs
- Google Cloud Speech / Text-to-Speech components
- Azure Speech components

### Retrieval and Knowledge

- Pinecone
- LangChain
- PDF processing
- text embeddings

### Data

- MongoDB
- Motor / PyMongo
- Redis components

### Infrastructure

- Docker
- Docker Compose
- Poetry
- environment-based configuration

## Repository Structure

A simplified view of the project:

```text
Call-system/
|
|-- main.py
|-- outbound_call.py
|-- mongo_config_manager.py
|-- mongo_trans.py
|-- pyproject.toml
|-- poetry.lock
|-- Dockerfile
|-- docker-compose.yml
|
|-- Pydantics_base_configs/
|   `-- Request and agent configuration models
|
|-- pinecone_configs/
|   |-- Pinecone configuration
|   |-- document embedding
|   `-- knowledge-base utilities
|
|-- Utilitiess/
|   `-- shared utilities and prompt logic
|
`-- additional telephony and configuration modules
```

## Installation

The project configuration currently supports Python versions:

```text
Python >= 3.9 and < 3.12
```

### 1. Clone the repository

```bash
git clone https://github.com/Nehalpk/Call-system.git
cd Call-system
```

### 2. Create a virtual environment

Using Python:

```bash
python -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

The project uses Poetry:

```bash
pip install poetry
poetry install
```

### 4. Configure environment variables

Create a `.env` file and provide the credentials required by the services you intend to use.

Example:

```env
BASE_URL=your_public_backend_url

OPENAI_API_KEY=your_openai_key

TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number

ELEVEN_LABS_API_KEY=your_elevenlabs_key

PINECONE_API_KEY=your_pinecone_key

MONGODB_URI=your_mongodb_connection_string
```

The exact variables required depend on which parts of the system are enabled.

**Never commit `.env` files, API keys, access tokens, or production credentials to the repository.**

### 5. Run the FastAPI service

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000
```

During development, reload mode can be used:

```bash
poetry run uvicorn main:app --reload --port 8000
```

## Example Use Cases

The architecture can support different conversational voice applications, including:

- AI customer-support agents
- appointment scheduling
- automated inbound reception
- outbound customer follow-up
- lead qualification
- business information assistants
- knowledge-based telephone assistants
- customer-preference collection
- live-transfer assistants
- voice agents integrated with external APIs

## Design Goals

The project focuses on several practical challenges involved in building conversational AI systems:

### Low-Latency Interaction

Telephone conversations require speech recognition, model inference, and speech synthesis to operate with low enough latency for natural interaction.

### Configurable Agents

Business-specific behaviour is stored as configuration rather than being permanently embedded in application logic.

### Tool-Using Agents

The conversational model can interact with external services instead of being limited to text generation.

### Knowledge Grounding

Retrieval components allow agents to use domain-specific information stored outside the language model.

### Real-Time Communication

WebSocket support enables conversation information to be exposed to live monitoring or frontend systems.

## Security

This repository is intended to demonstrate the architecture and implementation of an AI call system.

Production deployments should follow standard security practices, including:

- storing credentials only in environment variables or secret managers
- rotating exposed credentials immediately
- using authenticated API endpoints
- restricting CORS policies
- validating all external input
- encrypting sensitive data
- applying proper MongoDB access control
- restricting WebSocket access
- following privacy and consent requirements for call recording
- reviewing applicable telecommunication regulations

No production credentials should be committed to source control.

## Project Status

This repository represents an applied AI engineering project and includes experimental, integration, and development components.

It is provided primarily as a technical portfolio and research/software reference rather than as a packaged commercial product.

## Author

**Syed Nehal Hassan Shah**

GitHub: https://github.com/Nehalpk
