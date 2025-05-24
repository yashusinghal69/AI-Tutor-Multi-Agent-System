# 🎓 AI Tutor Multi-Agent System

A sophisticated AI-powered tutoring assistant built using multi-agent architecture principles inspired by Google's Agent Development Kit (ADK). The system intelligently routes educational queries to specialized subject-matter experts, each equipped with domain-specific tools to provide comprehensive learning assistance.

## 🏗️ Architecture Overview

### System Design

The AI Tutor follows a hierarchical multi-agent architecture with three main layers:

```
┌─────────────────────────────────────────────┐
│                 Web Interface               │
│            (FastAPI + HTML/JS)             │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│              Tutor Agent                    │
│         (Orchestrator/Router)               │
│    - Query Classification (Gemini API)     │
│    - Agent Selection & Delegation          │
│    - Response Coordination                 │
└─────────────────┬───────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐    ┌───▼───┐    ┌───▼───┐
│ Math  │    │Physics│    │ More  │
│ Agent │    │ Agent │    │Agents │
└───┬───┘    └───┬───┘    └───┬───┘
    │            │            │
┌───▼───┐    ┌───▼───┐    ┌───▼───┐
│ Tools │    │ Tools │    │ Tools │
│Layer  │    │Layer  │    │Layer  │
└───────┘    └───────┘    └───────┘
```

### Agent Types

#### 🎯 **Tutor Agent (Orchestrator)**

- **Role**: Central coordinator and user interface
- **Capabilities**:
  - Natural language query classification using Gemini API
  - Intelligent routing to appropriate specialist agents
  - Response aggregation and formatting
  - Session management and conversation history

#### 🔢 **Math Agent (Specialist)**

- **Domain**: Mathematics (Algebra, Calculus, Geometry, Statistics)
- **Tools**:
  - `CalculatorTool`: Advanced mathematical calculations
  - `GraphingTool`: Function plotting and visualization
  - `EquationSolverTool`: Symbolic equation solving
- **Capabilities**: Step-by-step problem solving, formula derivation, mathematical proofs

#### ⚛️ **Physics Agent (Specialist)**

- **Domain**: Physics (Mechanics, Thermodynamics, Electromagnetism, Quantum)
- **Tools**:
  - `PhysicsConstantsTool`: Scientific constants lookup
  - `UnitConverterTool`: Unit conversions and dimensional analysis
  - `PhysicsCalculatorTool`: Physics-specific calculations
- **Capabilities**: Concept explanation, problem solving, formula application

### 🛠️ Tools Layer

Each specialist agent is equipped with domain-specific tools that extend their capabilities:

- **Mathematical Tools**: Symbolic computation, graphing, statistical analysis
- **Physics Tools**: Constants database, unit conversion, simulation capabilities
- **Data Retrieval**: Web search integration for current information

## 🚀 Getting Started

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/ai-tutor-multi-agent.git
   cd ai-tutor-multi-agent
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**

   ```bash
   # Copy the example environment file
   copy .env.example .env
   # On Linux/Mac use: cp .env.example .env
   ```

   **IMPORTANT**: Edit the `.env` file with your actual configuration:

   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   REDIS_URL=redis://localhost:6379
   ENVIRONMENT=development
   ```

4. **Get Gemini API Key**

   - Visit [ai.google.dev](https://ai.google.dev)
   - Create a free account and generate an API key
   - **CRITICAL**: Replace `your_actual_gemini_api_key_here` in your `.env` file with the real API key


### Running the Application

**⚠️ IMPORTANT**: Make sure your `.env` file exists and contains a valid `GEMINI_API_KEY` before running!

1. **Create required directories**

   ```bash
   # Create missing directories for the application
   mkdir static
   mkdir templates
   mkdir logs

   # On Windows use:
   md static
   md templates
   md logs
   ```

2. **Verify environment setup**

   ```bash
   # Check if .env file exists
   dir .env
   # On Linux/Mac use: ls -la .env

   # Verify environment variables are loaded
   python -c "from config.settings import settings; print('API Key configured:', bool(settings.gemini_api_key))"
   ```

3. **Start the FastAPI server**

   ```bash
   cd "e:\AI Tutot Multi Agent System"
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the application**

   - Open your browser and navigate to: `http://localhost:8000`
   - The interactive web interface will be available for asking questions
   - You'll see a small indicator showing whether the app is using Redis or fallback storage


### Project Structure

Make sure your project structure looks like this:

```
AI Tutot Multi Agent System/
├── .env                     # Environment variables
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── api/
│   └── main.py            # FastAPI application
├── agents/
│   ├── tutor_agent.py     # Main orchestrator
│   ├── math_agent.py      # Math specialist
│   └── physics_agent.py   # Physics specialist
├── config/
│   └── settings.py        # Configuration
├── core/
│   ├── base_agent.py      # Agent base class
│   ├── base_tool.py       # Tool base class
│   └── state_manager.py   # Session management
├── tools/                 # Tool implementations
│   ├── calculator_tool.py
│   ├── equation_solver_tool.py
│   ├── graphing_tool.py
│   ├── physics_constants_tool.py
│   ├── unit_converter_tool.py
│   ├── physics_calculator_tool.py
│   └── web_search_tool.py
├── templates/             # HTML templates
│   └── index.html
├── static/               # Static files (CSS/JS)
└── logs/                 # Application logs
```

## 🌐 Live Deployment

**Live Application**: [https://ai-tutor-multi-agent.vercel.app](https://ai-tutor-multi-agent.vercel.app)


## 📊 Key Features

### ✅ Implemented

- [x] Multi-agent orchestration with Gemini API
- [x] Mathematics agent with calculation tools
- [x] Physics agent with constants and conversion tools
- [x] Web search integration for current information
- [x] Session management and conversation history
- [x] Modern web interface with real-time interaction
- [x] RESTful API with comprehensive documentation

## 🔧 Technical Stack

- **Backend**: FastAPI (Python)
- **AI/ML**: Google Gemini API
- **Database**: Redis (Session Management)
- **Frontend**: HTML5, TailwindCSS, Vanilla JavaScript
- **Tools**: Matplotlib, SymPy, NumPy, BeautifulSoup4
- **Deployment**: Vercel (Frontend), Railway (Backend)
