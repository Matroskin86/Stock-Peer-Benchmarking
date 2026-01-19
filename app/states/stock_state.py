import reflex as rx
import yfinance as yf
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from typing import Optional


class StockState(rx.State):
    """State for managing stock data and configuration."""

    ticker_input: str = ""
    selected_tickers: list[str] = [
        "AAPL",
        "MSFT",
        "AMZN",
        "NVDA",
        "TSLA",
        "GOOGL",
        "META",
    ]
    time_horizon: str = "1Y"
    stock_data: list[dict[str, str | float | None]] = []
    normalized_data: list[dict[str, str | float | None]] = []
    relative_strength_panels: list[
        dict[str, str | float | list[dict[str, str | float | None]]]
    ] = []
    loading: bool = False
    error_message: str = ""
    horizon_options: list[str] = ["1M", "3M", "6M", "1Y", "5Y", "10Y", "20Y"]
    best_ticker: str = ""
    best_change: float = 0.0
    worst_ticker: str = ""
    worst_change: float = 0.0
    palette: list[str] = [
        "#8b5cf6",
        "#10b981",
        "#f59e0b",
        "#3b82f6",
        "#ef4444",
        "#ec4899",
        "#06b6d4",
        "#84cc16",
        "#6366f1",
        "#f97316",
    ]
    table_sort_column: str = "Date"
    table_sort_asc: bool = False
    table_page: int = 1
    table_items_per_page: int = 15
    is_fullscreen: bool = False

    @rx.var
    def table_columns(self) -> list[str]:
        """Get column names from stock data."""
        if not self.stock_data:
            return []
        keys = list(self.stock_data[0].keys())
        if "Date" in keys:
            keys.remove("Date")
        return ["Date"] + sorted(keys)

    @rx.var
    def sorted_table_data(self) -> list[dict]:
        """Return sorted stock data."""
        if not self.stock_data:
            return []
        data = list(self.stock_data)
        col = self.table_sort_column
        asc = self.table_sort_asc

        @rx.event
        def sort_key(item):
            val = item.get(col)
            if val is None:
                return "" if isinstance(data[0].get(col, ""), str) else float("-inf")
            return val

        data.sort(key=sort_key, reverse=not asc)
        return data

    @rx.var
    def paginated_table_data(self) -> list[dict]:
        """Return paginated slice of sorted data."""
        start = (self.table_page - 1) * self.table_items_per_page
        end = start + self.table_items_per_page
        return self.sorted_table_data[start:end]

    @rx.var
    def table_total_pages(self) -> int:
        """Calculate total pages."""
        import math

        if not self.stock_data:
            return 0
        return math.ceil(len(self.stock_data) / self.table_items_per_page)

    @rx.var
    def ticker_metadata(self) -> list[dict[str, str]]:
        """Return list of dicts with ticker and assigned color."""
        return [
            {"ticker": ticker, "color": self.palette[i % len(self.palette)]}
            for i, ticker in enumerate(self.selected_tickers)
        ]

    @rx.var
    def best_change_formatted(self) -> str:
        return f"{self.best_change:+.2f}%"

    @rx.var
    def worst_change_formatted(self) -> str:
        return f"{self.worst_change:+.2f}%"

    @rx.var
    def has_data(self) -> bool:
        return len(self.normalized_data) > 0

    @rx.event
    def set_ticker_input(self, value: str):
        self.ticker_input = value

    @rx.event
    def add_ticker(self):
        """Add a ticker to the selected list."""
        if not self.ticker_input:
            return
        ticker = self.ticker_input.strip().upper()
        if ticker and ticker not in self.selected_tickers:
            self.selected_tickers.append(ticker)
            self.ticker_input = ""
            if self.has_data:
                return StockState.fetch_data
        elif ticker in self.selected_tickers:
            self.error_message = f"Ticker {ticker} is already selected."

    @rx.event
    def remove_ticker(self, ticker: str):
        """Remove a ticker from the selected list."""
        if ticker in self.selected_tickers:
            self.selected_tickers.remove(ticker)
            if self.has_data:
                return StockState.fetch_data

    @rx.event
    def set_time_horizon(self, horizon: str):
        """Set the analysis time horizon."""
        self.time_horizon = horizon

    @rx.event(background=True)
    async def fetch_data(self):
        """Fetch stock data from yfinance based on current configuration."""
        async with self:
            if not self.selected_tickers:
                self.error_message = "Please select at least one ticker."
                return
            self.loading = True
            self.error_message = ""
            self.stock_data = []
            self.normalized_data = []
        try:
            end_date = datetime.now()
            start_date = end_date
            days_map = {
                "1M": 30,
                "3M": 90,
                "6M": 180,
                "1Y": 365,
                "5Y": 365 * 5,
                "10Y": 365 * 10,
                "20Y": 365 * 20,
            }
            async with self:
                horizon_days = days_map.get(self.time_horizon, 365)
            start_date = end_date - timedelta(days=horizon_days)
            async with self:
                tickers_to_fetch = self.selected_tickers
            df = await asyncio.to_thread(
                yf.download,
                tickers=tickers_to_fetch,
                start=start_date,
                end=end_date,
                auto_adjust=True,
                progress=False,
            )
            if df.empty:
                raise ValueError("No data returned from provider.")
            close_data = df["Close"] if "Close" in df else df
            if isinstance(close_data, pd.Series):
                close_data = close_data.to_frame(name=tickers_to_fetch[0])
            close_data = close_data.ffill().dropna()
            if close_data.empty:
                raise ValueError("No valid price data found after processing.")
            raw_df = close_data.reset_index()
            raw_df["Date"] = raw_df["Date"].dt.strftime("%Y-%m-%d")
            raw_records = raw_df.to_dict("records")
            normalized_df = close_data / close_data.iloc[0]
            normalized_df = normalized_df.reset_index()
            normalized_df["Date"] = normalized_df["Date"].dt.strftime("%Y-%m-%d")
            norm_records = normalized_df.to_dict("records")
            b_ticker, b_change, w_ticker, w_change = ("", 0.0, "", 0.0)
            if not close_data.empty:
                start_vals = close_data.iloc[0]
                end_vals = close_data.iloc[-1]
                pct_changes = (end_vals / start_vals - 1.0) * 100
                b_ticker = pct_changes.idxmax()
                b_change = float(pct_changes.max())
                w_ticker = pct_changes.idxmin()
                w_change = float(pct_changes.min())
            panels = []
            if len(tickers_to_fetch) > 1 and (not close_data.empty):
                norm_numeric = close_data / close_data.iloc[0]
                for i, ticker in enumerate(tickers_to_fetch):
                    peers = [t for t in tickers_to_fetch if t != ticker]
                    if not peers:
                        continue
                    peer_avg_series = norm_numeric[peers].mean(axis=1)
                    stock_series = norm_numeric[ticker]
                    diff_series = stock_series - peer_avg_series
                    mx = float(diff_series.max())
                    mn = float(diff_series.min())
                    if pd.isna(mx) or pd.isna(mn) or mx == mn:
                        offset = 0.5
                    elif mx <= 0:
                        offset = 0.0
                    elif mn >= 0:
                        offset = 1.0
                    else:
                        offset = mx / (mx - mn)
                    panel_data_points = []
                    dates_str = diff_series.index.strftime("%Y-%m-%d")
                    for dt, st_val, pr_val, df_val in zip(
                        dates_str, stock_series, peer_avg_series, diff_series
                    ):
                        panel_data_points.append(
                            {
                                "Date": dt,
                                "Stock": float(st_val) if not pd.isna(st_val) else None,
                                "Peer": float(pr_val) if not pd.isna(pr_val) else None,
                                "Diff": float(df_val) if not pd.isna(df_val) else None,
                            }
                        )
                    current_diff = float(diff_series.iloc[-1])
                    panels.append(
                        {
                            "ticker": ticker,
                            "color": self.palette[i % len(self.palette)],
                            "current_diff": current_diff,
                            "current_diff_fmt": f"{current_diff:+.2%}",
                            "gradient_offset": offset,
                            "data": panel_data_points,
                        }
                    )
            async with self:
                self.stock_data = raw_records
                self.normalized_data = norm_records
                self.relative_strength_panels = panels
                self.best_ticker = str(b_ticker)
                self.best_change = b_change
                self.worst_ticker = str(w_ticker)
                self.worst_change = w_change
                self.loading = False
                self.table_page = 1
        except Exception as e:
            import logging

            logging.exception(f"Error fetching stock data: {e}")
            async with self:
                self.error_message = f"Failed to fetch data: {str(e)}"
                self.loading = False

    @rx.event
    def sort_table(self, col: str):
        if self.table_sort_column == col:
            self.table_sort_asc = not self.table_sort_asc
        else:
            self.table_sort_column = col
            self.table_sort_asc = True

    @rx.event
    def set_table_page(self, page: int):
        if 1 <= page <= self.table_total_pages:
            self.table_page = page

    @rx.event
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen

    @rx.event
    def download_csv(self):
        if not self.stock_data:
            return
        df = pd.DataFrame(self.stock_data)
        cols = self.table_columns
        cols = [c for c in cols if c in df.columns]
        csv_string = df[cols].to_csv(index=False)
        return rx.download(data=csv_string, filename="stock_peer_analysis.csv")