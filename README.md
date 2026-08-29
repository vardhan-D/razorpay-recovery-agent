# RecoveryOS

AI-powered recurring payment recovery agent built for Razorpay Buildathon.

## Problem

Recurring payments fail for many reasons:
- bank downtime
- insufficient funds
- expired mandates
- authentication failures
- technical failures

Blind retries can hurt conversion and customer experience.

RecoveryOS diagnoses each failed payment and chooses the safest recovery path.

## How It Works

1. Razorpay webhook detects a failed recurring payment.
2. RecoveryOS creates a recovery case.
3. Llama 3.2 diagnoses the failure and recommends an action.
4. A deterministic safety layer validates or overrides the recommendation.
5. Recovery tools execute the approved action.
6. Recovery state and audit history are stored in SQLite.
7. The dashboard tracks revenue at risk and recovered revenue.

## Example

Expired mandate:

AI recommendation:
Escalate

Safety layer:
Override

Final action:
Create Razorpay Payment Link

## Architecture

React
↓
FastAPI
↓
Recovery Agent
├── Llama 3.2
├── Safety Validator
├── Tool Router
├── Razorpay
└── SQLite

## Tech Stack

- React + Vite
- FastAPI
- Python
- SQLite
- SQLAlchemy
- Razorpay Test Mode
- Ollama
- Llama 3.2

## Key Features

- Razorpay webhook ingestion
- signature verification
- structured failure diagnosis
- AI recovery decisions
- deterministic safety guardrails
- bounded agent execution
- real Razorpay Payment Link creation
- explainable audit timeline
- revenue recovery dashboard
- persistent recovery cases

## Safety Design

The LLM never directly executes financial actions.

AI proposes.
Deterministic code validates.
Backend tools execute.

## Running Locally

### Backend

cd backend
venv\Scripts\activate
uvicorn app.main:app --reload

### Ollama

ollama run llama3.2

### Frontend

cd frontend
npm install
npm run dev

