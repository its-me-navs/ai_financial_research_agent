import streamlit as st
import plotly.graph_objects as go
from backend.agents.stock_agent import run_agent
from backend.tools.stock_tools import get_historical_data
from configs.settings import INDIAN_STOCKS

st.set_page_config(
    page_title="AI Financial Research Agent",
    page_icon="📈",
    layout="centered"
)

st.title("📈 AI Financial Research Agent")
st.caption("Real-time Indian stock market research powered by Groq AI")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

def detect_ticker(text: str):
    """Detect if a stock ticker is mentioned in the text."""
    text_upper = text.upper()
    for name, ticker in INDIAN_STOCKS.items():
        if name in text_upper or ticker in text_upper:
            return ticker
    return None

def render_chart(ticker: str):
    """Render a Plotly line chart for the given ticker."""
    data = get_historical_data(ticker, "1mo")
    if "error" in data:
        return
    dates = [d["date"] for d in data["data"]]
    closes = [d["close"] for d in data["data"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=closes,
        mode="lines",
        line=dict(color="#00C853", width=2),
        fill="tozeroy",
        fillcolor="rgba(0, 200, 83, 0.1)"
    ))
    fig.update_layout(
        title=f"{ticker} — Last 1 Month",
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        template="plotly_dark",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Suggested questions
if not st.session_state.messages:
    st.markdown("**Try asking:**")
    suggestions = [
        "What is Reliance's current stock price?",
        "Compare TCS and Infosys",
        "Show HDFC Bank's last month performance",
        "Tell me about Wipro as a company",
    ]
    cols = st.columns(2)
    for i, s in enumerate(suggestions):
        if cols[i % 2].button(s, use_container_width=True):
            st.session_state.pending = s
            st.rerun()

def handle_response(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Fetching real-time data..."):
            response, st.session_state.chat_session = run_agent(
                prompt, st.session_state.chat_session
            )
        st.markdown(response)
        # Auto-render chart if stock is mentioned
        ticker = detect_ticker(prompt)
        if ticker:
            render_chart(ticker)
    st.session_state.messages.append({"role": "assistant", "content": response})

if "pending" in st.session_state:
    prompt = st.session_state.pop("pending")
    handle_response(prompt)
    st.rerun()

if prompt := st.chat_input("Ask about any stock..."):
    handle_response(prompt)

# Sidebar
with st.sidebar:
    st.markdown("### 🇮🇳 Indian Stocks")
    st.code("Reliance → RELIANCE.NS\nTCS → TCS.NS\nInfosys → INFY.NS\nHDFC → HDFCBANK.NS")
    st.markdown("### 📊 Indices")
    st.code("Nifty 50 → ^NSEI\nSensex → ^BSESN")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()