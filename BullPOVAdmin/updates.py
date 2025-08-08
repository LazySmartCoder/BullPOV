import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import yfinance as yf

conn = psycopg2.connect(
    dsn="postgresql://neondb_owner:npg_7EQwSHtZf4qk@ep-restless-smoke-afl567fd-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)
cursor = conn.cursor(cursor_factory=RealDictCursor)

def declareResults():
    cursor.execute("""
        SELECT *, ("UPUsers" + "DownUsers") AS total_votes
        FROM "BullPOVApp_stock"
        WHERE ("UPUsers" + "DownUsers") > 0
    """)
    stocks = cursor.fetchall()

    for stock in stocks:
        stock_id = stock['id']
        previous_today = stock['PreviousCloseToday']
        previous_yesterday = stock['PreviousCloseYesterday']

        totaluplose = 0
        totaldownlose = 0

        # Determine outcome
        if previous_today > previous_yesterday:
            winning_prediction = True
        elif previous_today < previous_yesterday:
            winning_prediction = False
        else:
            winning_prediction = None

        if winning_prediction is None:
            for prediction in [True, False]:
                cursor.execute("""
                    SELECT * FROM "BullPOVApp_trade"
                    WHERE "Stock_id" = %s AND "Prediction" = %s AND "ActiveStatus" = TRUE
                """, (stock_id, prediction))
                trades = cursor.fetchall()

                for trade in trades:
                    trader_id = trade['Trader_id']
                    amount = trade['Amount']

                    cursor.execute("""
                        UPDATE "BullPOVApp_trade"
                        SET "Return" = 0.0, "Outcome" = TRUE, "ActiveStatus" = FALSE
                        WHERE id = %s
                    """, (trade['id'],))

                    cursor.execute("""
                        UPDATE "BullPOVApp_userdetail"
                        SET "InvestedBalance" = "InvestedBalance" - %s,
                            "WalletBalance" = "WalletBalance" + %s
                        WHERE "User_id" = %s
                    """, (amount, amount, trader_id))

        else:
            # Separate winning and losing trades
            cursor.execute("""
                SELECT * FROM "BullPOVApp_trade"
                WHERE "Stock_id" = %s AND "Prediction" = %s AND "ActiveStatus" = TRUE
            """, (stock_id, not winning_prediction))
            losing_trades = cursor.fetchall()

            cursor.execute("""
                SELECT * FROM "BullPOVApp_trade"
                WHERE "Stock_id" = %s AND "Prediction" = %s AND "ActiveStatus" = TRUE
            """, (stock_id, winning_prediction))
            winning_trades = cursor.fetchall()

            total_losing_amt = sum([t['Amount'] for t in losing_trades])
            total_winning_amt = sum([t['Amount'] for t in winning_trades]) or 1  # prevent div by zero
            total_pool = total_losing_amt + total_winning_amt

            # ---------------------------------------
            # Start Added: All users correct check
            # If there are no losers, return everyone’s amount with no return.
            if total_losing_amt == 0:
                for trade in winning_trades:
                    trader_id = trade['Trader_id']
                    amount = trade['Amount']

                    cursor.execute("""
                        UPDATE "BullPOVApp_trade"
                        SET "Return" = 0.0, "Outcome" = TRUE, "ActiveStatus" = FALSE
                        WHERE id = %s
                    """, (trade['id'],))

                    cursor.execute("""
                        UPDATE "BullPOVApp_userdetail"
                        SET "InvestedBalance" = "InvestedBalance" - %s,
                            "WalletBalance" = "WalletBalance" + %s
                        WHERE "User_id" = %s
                    """, (amount, amount, trader_id))
                continue  # Skip to next stock
            # End Added
            # ---------------------------------------

            # Calculate cut
            win_lose_ratio = total_winning_amt / total_losing_amt if total_losing_amt != 0 else float('inf')
            platform_cut_percent = 0.03 if win_lose_ratio >= 9 else 0.10
            platform_cut = platform_cut_percent * total_pool
            distributable_pool = total_losing_amt - platform_cut

            # Mark losing trades
            for trade in losing_trades:
                trader_id = trade['Trader_id']
                amount = trade['Amount']

                cursor.execute("""
                    UPDATE "BullPOVApp_userdetail"
                    SET "InvestedBalance" = "InvestedBalance" - %s
                    WHERE "User_id" = %s
                """, (amount, trader_id))

                cursor.execute("""
                    UPDATE "BullPOVApp_trade"
                    SET "Return" = 0.0, "Outcome" = FALSE, "ActiveStatus" = FALSE
                    WHERE id = %s
                """, (trade['id'],))

            # Distribute rewards to winners
            for trade in winning_trades:
                trader_id = trade['Trader_id']
                amount = trade['Amount']
                user_percent = amount / total_winning_amt
                user_return = int(user_percent * distributable_pool)

                cursor.execute("""
                    UPDATE "BullPOVApp_trade"
                    SET "Return" = %s, "Outcome" = TRUE, "ActiveStatus" = FALSE
                    WHERE id = %s
                """, (user_return, trade['id']))

                cursor.execute("""
                    UPDATE "BullPOVApp_userdetail"
                    SET "InvestedBalance" = "InvestedBalance" - %s,
                        "WalletBalance" = "WalletBalance" + %s + %s
                    WHERE "User_id" = %s
                """, (amount, amount, user_return, trader_id))

        # Reset votes
        cursor.execute("""
            UPDATE "BullPOVApp_stock" SET "UPUsers" = 0, "DownUsers" = 0 WHERE id = %s
        """, (stock_id,))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Results Declared!")

def update_all_stocks():

    cursor.execute("""SELECT "id", "Symbol", "PreviousCloseToday" FROM "BullPOVApp_stock" """)
    stocks = cursor.fetchall()

    count = 0
    for stock in stocks:
        symbol = stock['Symbol']
        stock_id = stock['id']
        previous_close_today = stock['PreviousCloseToday'] or 0

        try:
            ticker = yf.Ticker(f"{symbol}.BO")
            info = ticker.info

            current_price = info.get('currentPrice', 0)
            open_price = info.get('open', 0)
            day_high = info.get('dayHigh', 0)
            day_low = info.get('dayLow', 0)
            previous_close = info.get('previousClose', 0)
            price_change = round(current_price - previous_close, 2)
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
                previous_close_today, previous_close, price_change,
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