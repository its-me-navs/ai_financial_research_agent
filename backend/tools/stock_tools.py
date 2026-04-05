import yfinance as yf
from configs.settings import INDIAN_STOCKS


def _resolve_ticker(ticker: str) -> str:
    """Resolve common names to NSE ticker symbols."""
    ticker = ticker.upper().strip()
    return INDIAN_STOCKS.get(ticker, ticker)


def get_stock_price(ticker: str) -> dict:
    """
    Get current stock price and key stats for an Indian or global stock.
    Args:
        ticker: Stock ticker e.g. RELIANCE, TCS, RELIANCE.NS, AAPL
    Returns:
        dict with price, change, market cap, 52w high/low, volume
    """
    ticker = _resolve_ticker(ticker)
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev = info.get("previousClose", 0)
        return {
            "ticker": ticker,
            "name": info.get("longName", ticker),
            "current_price": current,
            "previous_close": prev,
            "change": round(current - prev, 2),
            "change_percent": round(((current - prev) / prev) * 100, 2) if prev else 0,
            "market_cap": info.get("marketCap"),
            "volume": info.get("volume"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "currency": info.get("currency", "INR"),
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}


def get_historical_data(ticker: str, period: str = "1mo") -> dict:
    """
    Get historical OHLCV data for a stock.
    Args:
        ticker: Stock ticker symbol
        period: One of 1d, 5d, 1mo, 3mo, 6mo, 1y
    Returns:
        dict with list of date, open, high, low, close, volume
    """
    ticker = _resolve_ticker(ticker)
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if hist.empty:
            return {"error": f"No historical data found for {ticker}"}
        return {
            "ticker": ticker,
            "period": period,
            "data": [
                {
                    "date": str(date.date()),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"]),
                }
                for date, row in hist.iterrows()
            ],
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}


def get_company_info(ticker: str) -> dict:
    """
    Get company fundamentals and description.
    Args:
        ticker: Stock ticker symbol
    Returns:
        dict with sector, industry, PE ratio, dividend yield, description
    """
    ticker = _resolve_ticker(ticker)
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name": info.get("longName"),
            "ticker": ticker,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "description": info.get("longBusinessSummary", "")[:600],
            "employees": info.get("fullTimeEmployees"),
            "website": info.get("website"),
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
            "roe": info.get("returnOnEquity"),
            "revenue": info.get("totalRevenue"),
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}
