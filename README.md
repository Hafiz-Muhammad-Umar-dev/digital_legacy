# 🧬 Digital Legacy — AI-Powered Digital Persona Platform

<p align="center">
  <strong>Preserving Memories. Maintaining Connections. Keeping Stories Alive.</strong>
</p>

<p align="center">
  An AI-powered digital legacy platform designed to preserve personal memories, personality traits, life experiences, and family relationships through interactive digital personas.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" />
  <img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white" />
  <img src="https://img.shields.io/badge/AI-Powered-8A2BE2?style=for-the-badge" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Architecture-Layered%20Monolith-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Testing-Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white" />
  <img src="https://img.shields.io/badge/API-REST-FF6C37?style=flat-square" />
</p>

---

## 📖 Overview

Digital Legacy is an AI-powered platform designed to transform personal memories into structured, searchable knowledge that enables families to interact with AI-powered representations of their loved ones in a meaningful, natural, and memory-grounded way.

The platform combines Large Language Models (LLMs), structured persona profiles, memory management, conversational AI, and multimedia processing to create personalized digital experiences.

### 💡 The Vision

**Preserve memories. Maintain connections. Keep stories alive.**

Digital Legacy is designed around one central idea: making personal memories accessible across generations through intelligent digital representations.

Users can create digital personas representing loved ones, configure their identities and personalities, store meaningful memories, and interact with them through AI-powered conversations.

For example, a family can create a digital persona representing their grandfather and configure family relationships such as:

- Grandfather → Grandson
- Grandfather → Granddaughter
- Father → Son
- Mother → Daughter

When a family member interacts with the persona, the system can use configured identity information and approved memories to provide more context-aware responses.

The platform is designed to prioritize factual grounding, personality consistency, and transparent AI reconstruction.

---

## ✨ Core Features

### 👤 1. Digital Persona Management

Create and manage personalized digital identities using structured persona information.

- Persona name and biography
- Personality traits
- Speaking style
- Preferred language
- Profile and portrait information
- Persona ownership and access control

### 👨‍👩‍👧‍👦 2. Structured Family Relationship Engine

A dedicated relationship system connects digital personas with their family members.

**Current implementation includes:**

- Structured family relationship records
- Member names
- Relationship types
- Preferred names
- Biographical notes
- Optional linked user accounts
- Relationship verification status
- Persona ownership validation

**Example:**

```yaml
Persona: Dada Jan

Known Family Relationships:
    Muhammad Umar → Grandson
    Preferred Name → Umar
```

These records are integrated into the persona's conversational context to improve relationship recognition.

### 🤖 3. AI-Powered Conversations

Interact with digital personas through contextual AI conversations.

- Persona-aware system prompts
- Conversation history
- Personality and speaking-style instructions
- Context-aware responses
- LLM provider abstraction
- Conversation persistence
- AI usage tracking

### 🧠 4. Memory Management

Preserve meaningful life experiences and personal information.

- Manual memory creation
- Memory categorization
- Memory approval workflow
- Memory editing
- Memory rejection
- Confidence tracking
- Source tracking

Only approved memories are intended to be used as factual context in persona conversations.

### 🎥 5. Video Transcription & Memory Extraction

The backend supports a multimedia processing pipeline for extracting memories from uploaded videos.

**Processing workflow:**

1. Upload a video.
2. Process the video through a background worker.
3. Generate a transcript using speech recognition.
4. Extract potential autobiographical memories using an LLM.
5. Store extracted memories for review.
6. Approve relevant memories before using them in conversations.

### 🎙️ 6. Voice & Audio Capabilities

The platform includes foundational audio functionality:

- Text-to-speech generation
- Speech transcription
- Voice-based chat endpoints
- Audio file management

> **Note:** Voice cloning is not currently part of the implemented feature set.

### 🔐 7. Authentication & Security

Security is integrated into the backend architecture.

- JWT authentication
- Access and refresh tokens
- Refresh token rotation and revocation
- Password hashing
- Persona ownership validation
- Memory ownership validation
- Relationship ownership validation
- API rate limiting

---

## 🏗️ System Architecture

Digital Legacy follows a modular layered-monolith architecture built with FastAPI and SQLAlchemy.

### 🔄 High-Level Architecture

```text
                    CLIENT APPLICATION
                           |
                           |
                     FASTAPI BACKEND
                           |
          +----------------+----------------+
          |                |                |
      AUTHENTICATION    PERSONAS         MEMORIES
          |                |                |
          |                |                |
          +----------------+----------------+
                           |
                 RELATIONSHIP ENGINE
                           |
                           |
                  CONVERSATION SERVICE
                           |
                 +---------+---------+
                 |                   |
             AI PROVIDERS       MEMORY SEARCH
                 |                   |
          +------+-------+           |
          |      |       |           |
       OpenRouter Ollama Mock    Approved Memories
                 |
                 |
              LLM OUTPUT
                 |
                 |
          CONVERSATION STORAGE


              BACKGROUND PROCESSING
                       |
                VIDEO PROCESSING
                       |
                 TRANSCRIPTION
                       |
                MEMORY EXTRACTION
                       |
                 REVIEW WORKFLOW
```

### 📦 Backend Architecture

| Component | Responsibility |
|:---|:---|
| `app/main.py` | FastAPI application and API endpoints |
| `app/models/` | SQLAlchemy database models |
| `app/schemas.py` | Pydantic request and response schemas |
| `app/routers/` | API route organization |
| `app/services/` | Business logic and conversational orchestration |
| `app/ai/` | LLM provider abstraction |
| `app/dependencies.py` | Authentication and ownership dependencies |
| `app/security.py` | Authentication and token security |
| `app/worker.py` | Background processing |
| `alembic/` | Database schema migrations |
| `tests/` | Automated testing |

---

## 🛠️ Technology Stack

Digital Legacy uses a modular Python backend with AI provider abstraction, relational database management, speech processing, and automated testing.

| Category | Technologies |
|:---|:---|
| **Backend** | Python, FastAPI |
| **Database** | SQLite |
| **ORM** | SQLAlchemy 2.0 |
| **Migrations** | Alembic |
| **Validation** | Pydantic v2 |
| **Authentication** | JWT, bcrypt |
| **AI Integration** | OpenRouter, Ollama, Mock Provider |
| **AI Models** | Configurable LLM providers |
| **Speech Recognition** | faster-whisper |
| **Text-to-Speech** | edge-tts |
| **Background Processing** | Python background worker |
| **Testing** | Pytest, FastAPI TestClient |

---

## 🗄️ Database Architecture

The backend uses a relational database architecture.

### 📋 Database Entities

Current database entities include:

- Users
- Refresh Tokens
- Personas
- Persona Relationships
- Memories
- Conversations
- Media Assets
- Processing Jobs
- Video Transcripts
- AI Usage

### 👨‍👩‍👧 Persona Relationship Model

The relationship engine introduces a dedicated `persona_relationships` table.

**Important fields include:**

| Field | Description |
|:---|:---|
| `id` | Unique relationship identifier |
| `persona_id` | Associated persona |
| `member_name` | Family member's name |
| `relationship_type` | Relationship with the persona |
| `preferred_name` | Preferred way to address the member |
| `biographical_notes` | Additional relationship context |
| `linked_user_id` | Optional linked account |
| `verification_status` | Relationship record verification status |
| `created_at` | Creation timestamp |
| `updated_at` | Last update timestamp |

Relationships are connected to personas through foreign keys and protected by ownership validation.

---

## 🔌 API Documentation

The backend exposes RESTful API endpoints.

Interactive API documentation is available through FastAPI Swagger UI.

| Resource | URL |
|:---|:---|
| **Backend Server** | `http://127.0.0.1:8000` |
| **Swagger UI** | `http://127.0.0.1:8000/docs` |
| **ReDoc** | `http://127.0.0.1:8000/redoc` |

### 📡 Core API Groups

| API Group | Functionality |
|:---|:---|
| Authentication | Registration, login, refresh, logout |
| Personas | Persona creation and retrieval |
| Relationships | Family relationship management |
| Memories | Memory creation, review, approval and retrieval |
| Conversations | Conversation history |
| Chat | AI-powered persona conversations |
| Videos | Video upload and processing |
| Voice | Voice chat and audio functionality |
| TTS | Text-to-speech generation |

### 👨‍👩‍👧 Relationship API Endpoints

| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/api/v1/personas/{persona_id}/relationships` | Create relationship |
| `GET` | `/api/v1/personas/{persona_id}/relationships` | List persona relationships |
| `GET` | `/api/v1/relationships/{relationship_id}` | Retrieve relationship |
| `PATCH` | `/api/v1/relationships/{relationship_id}` | Update relationship |
| `DELETE` | `/api/v1/relationships/{relationship_id}` | Delete relationship |

All relationship endpoints require authentication and enforce persona ownership.

---

## 🚀 Installation & Setup

Follow these steps to configure and run Digital Legacy locally.

### 📋 Prerequisites

Make sure the following tools are installed:

- Python 3.10 or newer
- pip
- Git
- SQLite
- An API key for the selected external LLM provider, if applicable

### 1️⃣ Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd digital-legacy
```

Navigate into the backend directory:

```bash
cd backend
```

### 2️⃣ Create a Virtual Environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the backend directory.

Configure the application settings according to `app/config.py`.

**Example configuration:**

```ini
DATABASE_URL=sqlite:///./digital_legacy.db

OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=your_model_name

SECRET_KEY=your_secret_key
```

Use the exact variable names expected by your current application configuration.

> **🔒 Security:** Never commit `.env` files, API keys, passwords, or production secrets to GitHub.

### 5️⃣ Apply Database Migrations

```bash
alembic upgrade head
```

### 6️⃣ Start the Backend Server

```bash
uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

**Swagger API Documentation:**

```text
http://127.0.0.1:8000/docs
```

---

## 🧪 Running Tests

Run the complete automated test suite:

```bash
python -m pytest -v
```

Run relationship-specific tests:

```bash
python -m pytest tests/test_relationships.py -v
```

### ✅ Test Coverage

The test suite is designed to validate:

- Relationship CRUD operations
- Persona ownership and security isolation
- Chat compatibility
- Existing persona compatibility
- Relationship-aware prompt integration

Additional prompt-inspection and greeting-recognition coverage is being developed.

---

## 🧠 AI & Memory Architecture

Digital Legacy separates personal identity, family relationships, approved memories, and conversational context.

### 👤 1. Identity Context

Stores relatively stable persona information:

- Name
- Biography
- Personality
- Speaking style
- Preferred language

### 👨‍👩‍👧 2. Relationship Context

Stores structured family information and relationship mappings.

### 📚 3. Memory Context

Stores personal experiences and factual information extracted from approved sources.

### 💬 4. Conversation Context

Maintains recent conversation history to support continuity.

This separation helps prevent temporary conversation details from being confused with verified personal memories.

### 🛡️ Anti-Hallucination Design

The system is designed to:

- Use approved memories as factual context.
- Recognize explicitly configured family relationships.
- Avoid inventing personal experiences.
- Distinguish known facts from unknown information.
- Preserve transparency about AI-generated reconstructions.

---

## 🗺️ Development Roadmap

Digital Legacy is being developed incrementally.

### 🟢 Phase 1 — Structured Identity & Relationship Engine

- Persona relationship database model
- Alembic migration
- Pydantic relationship schemas
- Authenticated relationship API endpoints
- Persona prompt integration
- Ownership and access control
- Initial automated tests
- Additional prompt-inspection tests
- Relationship-aware greeting tests

### 🔵 Phase 2 — Semantic Memory Retrieval

- Embedding generation
- Semantic memory search
- Hybrid retrieval
- Improved contextual memory selection
- Memory relevance evaluation

### 🟣 Phase 3 — Personality & Conversation Consistency

- Advanced personality modeling
- More natural conversational behavior
- Cross-session continuity improvements
- Conversation summarization
- Improved multilingual consistency

### 🟠 Phase 4 — Advanced Digital Legacy Capabilities

- Expanded multimedia memory ingestion
- Image and document memory processing
- Family collaboration
- Advanced voice capabilities
- Production-grade evaluation and monitoring

> **Note:** Roadmap items represent planned development, not necessarily available functionality.

---

## 🎯 Design Principles

Digital Legacy is being developed around five core principles:

### 1. 🧬 Identity Consistency

A digital persona should maintain its configured identity, personality, and relationships across conversations.

### 2. 🧠 Memory Grounding

Personal memories should be based on stored and approved information rather than generated assumptions.

### 3. 👨‍👩‍👧 Relationship Awareness

Family relationships should be explicitly structured and available to the conversational engine.

### 4. 🔐 Privacy & Ownership

Personal memories and digital personas must remain protected through authentication and access control.

### 5. 🤝 Transparent AI Reconstruction

Digital personas are AI-generated representations, not the actual deceased individuals. The platform should preserve this distinction while providing natural and respectful interactions.

---

## 📊 Project Status

**Phase 1 implemented — verification in progress**

The backend currently includes foundational persona management, memory processing, conversational AI, authentication, and structured family relationship capabilities.

Further development is focused on improving memory retrieval, personality consistency, and long-term conversational continuity.

---

## 🤝 Contributing

Contributions, technical suggestions, and architectural feedback are welcome.

Before submitting changes:

1. Review the existing architecture.
2. Preserve backward compatibility.
3. Follow existing coding conventions.
4. Add or update automated tests.
5. Never commit credentials or private user data.

---

## 📜 License

Add your chosen open-source or proprietary license before distributing this project publicly.

---

## ❤️ The Vision Behind Digital Legacy

Digital Legacy is built around the belief that personal stories, experiences, and memories deserve to be preserved.

Through structured memory systems, AI-powered conversations, and relationship-aware digital personas, the platform aims to create a bridge between generations.

**Technology can preserve information. Meaningful memories preserve connections.**

<p align="center">
  <strong>🧬 Digital Legacy</strong>
  <br/>
  <em>Preserving memories. Connecting generations. Keeping stories alive.</em>
</p>
