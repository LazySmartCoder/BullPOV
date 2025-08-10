import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import yfinance as yf
from datetime import datetime, timedelta

conn = psycopg2.connect(
    dsn="postgresql://neondb_owner:npg_7EQwSHtZf4qk@ep-weathered-lab-afllh2wd-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)
cursor = conn.cursor(cursor_factory=RealDictCursor)

def get_previous_date():
    yesterday = datetime.today() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def get_previous_close(symbol: str, date_str: str):
    # Parse the date
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    # Get one trading day before the target date
    prev_day = target_date - timedelta(days=1)
    ticker = yf.Ticker(symbol)
    # Fetch history from prev_day to target_date
    data = ticker.history(start=prev_day.strftime("%Y-%m-%d"), end=date_str, interval="1d")
    if not data.empty:
        # 'Close' column's last value is the previous close
        return data["Close"].iloc[-1]
    else:
        return 0  # No data (holiday, weekend, or invalid date)

def update_all_stocks():

    cursor.execute("""SELECT "id", "Symbol", "PreviousCloseToday" FROM "BullPOVApp_stock" """)
    stocks = cursor.fetchall()

    count = 0
    for stock in stocks:
        symbol = stock['Symbol']
        if symbol in ["NSEMDCP50", "CNXIT", "NSEBANK", "BSESN", "NSEI"]:
            continue
        stock_id = stock['id']
        previous_close_today = stock['PreviousCloseToday'] or 0

        try:
            ticker = yf.Ticker(f"{symbol}.BO")
            info = ticker.info

            current_price = info.get('currentPrice', 0)
            open_price = info.get('open', 0)
            day_high = info.get('dayHigh', 0)
            day_low = info.get('dayLow', 0)
            previous_close_yesterday = float(get_previous_close(f"{symbol}.BO", get_previous_date()))
            previous_close_today = info.get('previousClose', 0)
            price_change = round(current_price - previous_close_today, 2)
            volume = info.get('volume', 0)
            market_cap = info.get('marketCap', 0)
            pe_ratio = info.get('trailingPE', 0)
            dividend_yield = info.get('dividendYield', 0) or 0
            eps = info.get('trailingEps', 0)

            cursor.execute("""
                UPDATE "BullPOVApp_stock"
                SET "CurrentPrice" = %s,
                    "DayHigh" = %s,
                    "DayLow" = %s,
                    "OpeningPrice" = %s,
                    "PreviousCloseYesterday" = %s,
                    "PreviousCloseToday" = %s,
                    "PriceChange" = %s,
                    "Volume" = %s,
                    "MktCap" = %s,
                    "PERatio" = %s,
                    "DividendYield" = %s,
                    "EPS" = %s
                WHERE "id" = %s
            """, (
                current_price, day_high, day_low, open_price,
                previous_close_yesterday, previous_close_today, price_change,
                volume, market_cap, pe_ratio, dividend_yield, eps,
                stock_id
            ))

            count += 1
            print(f"✅ Updated {symbol} ({count})")

        except Exception as e:
            print(f"❌ Error updating {symbol}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All stocks updated.")
update_all_stocks()