import reflex as rx
from app.states.stock_state import StockState


def stat_card(
    title: str, ticker: str, change_str: str, value: float, is_inverse: bool = False
) -> rx.Component:
    is_positive = value >= 0
    color_class = rx.cond(is_positive, "text-emerald-600", "text-red-600")
    bg_class = rx.cond(
        is_positive, "bg-emerald-50 text-emerald-700", "bg-red-50 text-red-700"
    )
    icon_name = rx.cond(is_positive, "trending-up", "trending-down")
    icon_color = rx.cond(is_positive, "text-emerald-500", "text-red-500")
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                title,
                class_name="text-xs font-semibold text-gray-500 uppercase tracking-wider",
            ),
            rx.icon(icon_name, size=20, class_name=icon_color),
            class_name="flex justify-between items-center mb-3",
        ),
        rx.el.div(
            rx.el.h3(
                ticker, class_name="text-2xl font-bold text-gray-900 leading-tight"
            ),
            rx.el.span(
                change_str,
                class_name=rx.cond(
                    ticker != "",
                    f"text-xs font-bold px-2 py-1 rounded-full {bg_class}",
                    "hidden",
                ),
            ),
            class_name="flex items-center gap-3",
        ),
        class_name="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex-1 min-w-[240px]",
    )


def summary_stats() -> rx.Component:
    return rx.cond(
        StockState.has_data,
        rx.el.div(
            stat_card(
                "Best Performer",
                StockState.best_ticker,
                StockState.best_change_formatted,
                StockState.best_change,
            ),
            stat_card(
                "Worst Performer",
                StockState.worst_ticker,
                StockState.worst_change_formatted,
                StockState.worst_change,
            ),
            class_name="flex flex-col md:flex-row gap-4 w-full max-w-5xl mx-auto mt-6 animate-fade-in",
        ),
    )