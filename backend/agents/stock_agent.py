import json
import os
from groq import Groq
from dotenv import load_dotenv
from backend.tools.stock_tools import get_stock_price, get_historical_data, get_company_info

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an expert Indian stock market research assistant.
You help users with stock prices, financial analysis, and market information
for Indian stocks (NSE/BSE) and global markets.
Always use the available tools to fetch real-time data before answering.
Format prices in ₹ for Indian stocks and $ for US stocks.
Be concise, accurate, and helpful."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get current stock price and key stats for an Indian or global stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker e.g. RELIANCE, TCS, RELIANCE.NS"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_historical_data",
            "description": "Get historical OHLCV price data for a stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"},
                    "period": {"type": "string", "description": "Period: 1d, 5d, 1mo, 3mo, 6mo, 1y", "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y"]}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_info",
            "description": "Get company fundamentals like sector, PE ratio, description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"]
            }
        }
    }
]

TOOL_MAP = {
    "get_stock_price": get_stock_price,
    "get_historical_data": get_historical_data,
    "get_company_info": get_company_info,
}


def run_agent(user_message: str, chat_session=None):
    if chat_session is None:
        chat_session = []

    chat_session.append({"role": "user", "content": user_message})

    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + chat_session,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        # No tool call — final answer
        if not message.tool_calls:
            chat_session.append({"role": "assistant", "content": message.content})
            return message.content, chat_session

        # Handle tool calls
        chat_session.append({"role": "assistant", "content": message.content, "tool_calls": message.tool_calls})

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            result = TOOL_MAP[tool_name](**tool_args)
            chat_session.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })