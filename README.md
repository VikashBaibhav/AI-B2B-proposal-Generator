#  PropAI Gen — AI B2B Proposal Generator

> Instantly generate tailored, professional B2B sales proposals powered by Google Gemini AI. Input your prospect's details and receive a complete proposal with pricing tiers, ROI insights, and a compelling call to action — in seconds.

---

##  Features

-  **AI-Powered Proposals** — Uses Google Gemini to generate fully customized B2B proposals based on client industry, pain points, and goals
-  **Smart Pricing Engine** — Automatically calculates and recommends pricing tiers based on company size and budget
-  **Structured Output** — Every proposal includes executive summary, problem statement, proposed solution, key benefits, implementation timeline, cost breakdown, and call to action
-  **Budget Constraint Enforcement** — Scales pricing tiers proportionally if total cost exceeds the client's stated budget limit
-  **Proposal Preview & Export** — Clean, print-ready proposal preview page
-  **Schema Validation** — AI responses are validated against a strict JSON schema before being accepted
-  **Prompt Logging** — Full prompt/response logging for auditing and debugging
-  **Fast & Reactive** — React + Vite frontend, FastAPI async backend

---

##  Architecture

The project follows **Clean Architecture** principles, separating business logic from AI/infrastructure concerns.

```
AI B2B Proposal Generator/
├── backend/
│   ├── api/                    # FastAPI routers & request/response schemas
│   ├── application/
│   │   └── use_cases/          # Core business logic (GenerateProposal, CalculatePricing)
│   ├── domain/
│   │   ├── entities/           # Proposal, Client, PricingTier domain models
│   │   └── interfaces/         # Abstract contracts (AIService, ProposalRepository)
│   ├── infrastructure/
│   │   ├── ai/                 # Gemini AI service implementation
│   │   └── repositories/       # In-memory proposal store
│   ├── prompts/                # Prompt templates (proposal_generation.txt, pricing_analysis.txt)
│   ├── validators/             # JSON schema validation for AI responses
│   ├── logger/                 # Structured prompt/response logger
│   └── tests/                  # Pytest test suite
└── frontend/
    └── src/
        ├── pages/              # HomePage, ProposalFormPage, ProposalPreviewPage
        ├── components/         # Reusable UI components
        └── services/           # Axios API service layer
```

---

##  Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, React Router v7, Axios, Lucide React |
| **Backend** | FastAPI, Uvicorn, Python 3.11+ |
| **AI** | Google Gemini (`gemini-2.5-flash`) via `google-generativeai` SDK |
| **Testing** | Pytest, pytest-asyncio, HTTPX |

---

##  Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- A **Google AI Studio API key** → [Get one here](https://aistudio.google.com/app/apikey)

---

### 1. Clone the repository

```bash
git clone https://github.com/VikashBaibhav/AI-B2B-proposal-Generator
```

---

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Open `.env` and add your Google API key:

```env
GOOGLE_API_KEY=your-google-api-key-here
```

Start the backend server:

```bash
python main.py
```

The API will be available at **http://localhost:8000**
Interactive API docs at **http://localhost:8000/docs**

---

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The app will be available at **http://localhost:5173**

---



## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/proposals/generate` | Generate a new AI proposal |
| `GET` | `/api/proposals/{id}` | Retrieve a proposal by ID |
| `GET` | `/api/proposals/` | List all proposals |
| `GET` | `/docs` | Interactive Swagger UI |

---

## Running Tests

```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_proposal_validator.py -v
```

---


##  Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

##  License

This project is licensed under the MIT License.

---

##  Author

**Vikash**

---


