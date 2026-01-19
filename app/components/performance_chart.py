import reflex as rx
from app.states.stock_state import StockState


def custom_tooltip() -> rx.Component:
    return rx.recharts.graphing_tooltip(
        separator="",
        content_style={
            "backgroundColor": "rgba(255, 255, 255, 0.96)",
            "borderRadius": "12px",
            "boxShadow": "0 10px 15px -3px rgb(0 0 0 / 0.1)",
            "border": "1px solid #f3f4f6",
            "padding": "12px",
            "fontSize": "12px",
            "lineHeight": "1.5",
        },
        item_style={"padding": "2px 0", "color": "#4b5563", "fontWeight": "500"},
        label_style={
            "fontWeight": "700",
            "color": "#111827",
            "marginBottom": "8px",
            "display": "block",
        },
        cursor={"stroke": "#9ca3af", "strokeWidth": 1, "strokeDasharray": "4 4"},
    )


def render_line(item: dict[str, str]) -> rx.Component:
    return rx.recharts.line(
        data_key=item["ticker"],
        stroke=item["color"],
        type_="monotone",
        dot=False,
        stroke_width=2,
        active_dot={"r": 6, "strokeWidth": 0, "fill": item["color"]},
        connect_nulls=True,
    )


def chart_legend_item(item: dict[str, str]) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            class_name="w-2.5 h-2.5 rounded-full mr-2 shadow-sm",
            style={"backgroundColor": item["color"]},
        ),
        rx.el.span(item["ticker"], class_name="text-xs font-semibold text-gray-700"),
        class_name="flex items-center px-2.5 py-1.5 bg-white rounded-lg border border-gray-200 shadow-sm transition-transform hover:scale-105 select-none",
    )


def performance_chart() -> rx.Component:
    return rx.cond(
        StockState.has_data,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Relative Performance",
                        class_name="text-lg font-bold text-gray-900",
                    ),
                    rx.el.p(
                        "Normalized returns (Base = 1.0)",
                        class_name="text-xs font-medium text-gray-500 mt-0.5",
                    ),
                    class_name="flex flex-col",
                ),
                rx.el.div(
                    rx.foreach(StockState.ticker_metadata, chart_legend_item),
                    class_name="flex flex-wrap gap-2 mt-4 lg:mt-0 justify-start lg:justify-end",
                ),
                class_name="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-8 gap-4",
            ),
            rx.el.div(
                rx.recharts.line_chart(
                    rx.recharts.cartesian_grid(
                        stroke_dasharray="3 3", vertical=False, stroke="#f3f4f6"
                    ),
                    custom_tooltip(),
                    rx.recharts.x_axis(
                        data_key="Date",
                        hide=False,
                        axis_line=False,
                        tick_line=False,
                        min_tick_gap=40,
                        tick={"fontSize": 11, "fill": "#9ca3af", "fontWeight": "500"},
                        dy=10,
                    ),
                    rx.recharts.y_axis(
                        hide=False,
                        axis_line=False,
                        tick_line=False,
                        tick={"fontSize": 11, "fill": "#9ca3af", "fontWeight": "500"},
                        domain=["auto", "auto"],
                        width=40,
                    ),
                    rx.foreach(StockState.ticker_metadata, render_line),
                    data=StockState.normalized_data,
                    width="100%",
                    height="100%",
                    margin={"top": 5, "right": 5, "bottom": 5, "left": -10},
                ),
                class_name="h-[350px] w-full",
            ),
            class_name="bg-white p-6 md:p-8 rounded-2xl shadow-sm border border-gray-200 w-full max-w-5xl mx-auto mt-6 animate-fade-in",
        ),
    )