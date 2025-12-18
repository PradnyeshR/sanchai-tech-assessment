import os
import requests
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development simplicity, allow all. In production, be specific.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenRouter API Key configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY is not set in environment variables.")

# --- Tools ---
@tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a specific city. 
    Returns a string describing the temperature and weather code.
    """
    try:
        # Clean input if it comes as a JSON string (common with some agents)
        city = city.strip()
        if city.startswith("{") and city.endswith("}"):
            import json
            try:
                data = json.loads(city)
                if "city" in data:
                    city = data["city"]
                elif "location" in data:
                    city = data["location"]
                else:
                    # Take the first value if keys don't capture it
                    city = list(data.values())[0]
            except:
                pass
        
        # 1. Geocoding to get lat/long
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if not geo_res.get("results"):
            return f"Could not find coordinates for city: {city}"
            
        location = geo_res["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        name = location["name"]
        
        # 2. Weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
        weather_res = requests.get(weather_url).json()
        
        current = weather_res.get("current", {})
        temp = current.get("temperature_2m")
        unit = weather_res.get("current_units", {}).get("temperature_2m", "°C")
        
        # Simple weather code mapping (verified against OpenMeteo docs)
        # 0: Clear sky, 1, 2, 3: Mainly clear, partly cloudy, and overcast
        # Just return raw data for the LLM to interpret nicely
        
        return f"Weather in {name}: {temp}{unit}"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

# --- LangChain Agent Setup ---

# Initialize LLM with OpenRouter
# Using a widely available model like meta-llama/llama-3-8b-instruct or similar via OpenRouter
# Ideally, user should configure model name.
llm = ChatOpenAI(
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="mistralai/mistral-7b-instruct:free", # Using a highly available free model
)

tools = [get_weather]

# Use ReAct prompt which works better with generic models than function calling
try:
    prompt = hub.pull("hwchase17/react-chat")
except:
    # Fallback if hub pull fails or no API key for hub (though usually public)
    # Constructing a simple ReAct prompt manually if needed, but hub.pull is standard.
    # We will assume hub works or define a local prompt.
    from langchain_core.prompts import PromptTemplate
    template = '''Assistant is a large language model trained by OpenAI.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to enter into natural-sounding conversations with a human.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

TOOLS:
------

Assistant has access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}'''
    prompt = PromptTemplate.from_template(template)

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# --- API Endpoints ---

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Run the agent
        result = agent_executor.invoke({
            "input": request.message,
            "chat_history": [] # Stateless for now, or could implement memory
        })
        return ChatResponse(response=result["output"])
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
