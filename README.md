# SanchAI Analytics Tech Assessment - Weather Bot

**Submitted By:**
*   **Name:** Pradnyesh Ajaykumar Ravane
*   **College PRN:** 12211683
*   **Roll No:** 52
*   **Branch:** CSAI - A

## Overview
This is a minimal web application built for the SanchAI Analytics implementation internship assessment. It features a **React** frontend and a **FastAPI** backend that utilizes **LangChain** and **OpenRouter** to answer user queries about the weather.

The system uses a **ReAct Agent** equipped with a custom `get_weather` tool (using the OpenMeteo API) to fetch real-time weather data for any city.

![App Screenshot](screenshot.png)

## Features
*   **Modern Chat UI**: Clean, responsive interface built with React and polished CSS.
*   **AI Agent**: Backend powered by `mistral7b-instruct` (via OpenRouter) to understand natural language queries.
*   **Weather Tool**: Custom tool integration to fetch accurate temperature and weather conditions without needing an API key for the weather provider.
*   **Robust Handling**: The backend intelligently processes inputs, handling both plain text and JSON-formatted responses from the LLM.

## Tech Stack
*   **Frontend**: React, Vite, Axios, CSS Modules.
*   **Backend**: FastAPI, Uvicorn, Python 3.9+.
*   **AI/LLM**: LangChain, OpenRouter (Mistral 7B).
*   **External APIs**: OpenMeteo (Geocoding & Weather).

## Setup Instructions

### Prerequisites
*   Node.js & npm
*   Python 3.8+
*   An OpenRouter API Key

### 1. Backend Setup
Navigate to the backend directory:
```bash
cd backend
```

Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
pip install langchainhub
```

Configure Environment Variables:
Create a `.env` file in the `backend` directory and add your key:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Start the Backend Server:
```bash
uvicorn main:app --reload
```
The backend will run at `http://localhost:8000`.

### 2. Frontend Setup
Navigate to the frontend directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

Start the Development Server:
```bash
npm run dev
```
The frontend will run at `http://localhost:5173`.

## Usage
1.  Open `http://localhost:5173` in your browser.
2.  Type a query like *"What is the weather in Mumbai?"* or *"Temperature in New York"*.
3.  The agent will "think" (invoke the weather tool) and respond with the current weather.
