import reflex as rx
from app.states.stock_state import StockState


def ticker_chip(ticker: str) -> rx.Component:
    return rx.el.div(
        rx.el.span(ticker, class_name="font-semibold text-sm text-violet-700"),
        rx.el.button(
            rx.icon("x", size=14, class_name="text-violet-500 hover:text-violet-900"),
            on_click=lambda: StockState.remove_ticker(ticker),
            class_name="ml-2 p-0.5 rounded-full hover:bg-violet-100 transition-colors cursor-pointer flex items-center justify-center",
        ),
        class_name="bg-violet-50 border border-violet-200 rounded-full px-3 py-1 flex items-center shadow-sm",
    )


def horizon_button(horizon: str) -> rx.Component:
    is_selected = StockState.time_horizon == horizon
    return rx.el.button(
        horizon,
        on_click=lambda: StockState.set_time_horizon(horizon),
        class_name=rx.cond(
            is_selected,
            "px-3 py-1.5 text-sm font-medium rounded-lg bg-violet-600 text-white shadow-md transition-all",
            "px-3 py-1.5 text-sm font-medium rounded-lg bg-white text-gray-600 border border-gray-200 hover:bg-gray-50 hover:border-gray-300 transition-all",
        ),
    )


def config_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Stock Peer Analysis", class_name="text-2xl font-bold text-gray-900"
            ),
            rx.el.p(
                "Compare historical performance normalized to a common baseline.",
                class_name="text-gray-500 text-sm mt-1",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Tickers",
                    class_name="block text-sm font-semibold text-gray-700 mb-2",
                ),
                rx.el.div(
                    rx.el.input(
                        placeholder="Enter symbol (e.g. MSFT)",
                        on_change=StockState.set_ticker_input,
                        on_key_down=lambda key: rx.cond(
                            key == "Enter", StockState.add_ticker, rx.noop()
                        ),
                        class_name="flex-1 min-w-[120px] px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none transition-all text-sm uppercase placeholder:normal-case",
                        default_value=StockState.ticker_input,
                    ),
                    rx.el.button(
                        rx.icon("plus", size=18),
                        "Add",
                        on_click=StockState.add_ticker,
                        class_name="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors text-sm font-medium flex items-center gap-2",
                    ),
                    class_name="flex gap-2 mb-3",
                ),
                rx.el.div(
                    rx.foreach(StockState.selected_tickers, ticker_chip),
                    class_name="flex flex-wrap gap-2 min-h-[40px] p-2 bg-gray-50/50 rounded-lg border border-dashed border-gray-200",
                ),
                class_name="flex flex-col",
            ),
            rx.el.div(
                class_name="h-px bg-gray-200 w-full my-6 md:my-0 md:h-auto md:w-px"
            ),
            rx.el.div(
                rx.el.label(
                    "Time Horizon",
                    class_name="block text-sm font-semibold text-gray-700 mb-2",
                ),
                rx.el.div(
                    rx.foreach(StockState.horizon_options, horizon_button),
                    class_name="flex flex-wrap gap-2 mb-6",
                ),
                rx.el.button(
                    rx.cond(
                        StockState.loading,
                        rx.el.div(
                            rx.spinner(size="1", class_name="text-white"),
                            rx.el.span("Fetching Data...", class_name="ml-2"),
                            class_name="flex items-center",
                        ),
                        rx.el.div(
                            rx.icon("line-chart", size=18),
                            rx.el.span("Analyze Performance", class_name="ml-2"),
                            class_name="flex items-center",
                        ),
                    ),
                    on_click=StockState.fetch_data,
                    disabled=StockState.loading,
                    class_name="w-full md:w-auto px-6 py-3 bg-violet-600 text-white rounded-xl hover:bg-violet-700 disabled:opacity-70 disabled:cursor-not-allowed transition-all shadow-lg shadow-violet-200 font-semibold flex justify-center items-center",
                ),
                class_name="flex flex-col justify-between",
            ),
            class_name="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-6",
        ),
        rx.cond(
            StockState.error_message != "",
            rx.el.div(
                rx.icon("cigarette", size=20, class_name="text-red-500 mr-2"),
                rx.el.p(
                    StockState.error_message,
                    class_name="text-red-700 text-sm font-medium",
                ),
                class_name="mt-4 p-4 bg-red-50 border border-red-100 rounded-xl flex items-center animate-fade-in",
            ),
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 w-full max-w-5xl mx-auto",
    )