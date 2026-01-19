import reflex as rx
from app.states.stock_state import StockState


def define_gradient(ticker: str, offset: float) -> rx.Component:
    """Define a linear gradient for the area chart based on data offset."""
    return rx.el.svg.defs(
        rx.el.svg.linear_gradient(
            rx.el.svg.stop(offset="0", stop_color="#10b981", stop_opacity=0.6),
            rx.el.svg.stop(offset=offset, stop_color="#10b981", stop_opacity=0.1),
            rx.el.svg.stop(offset=offset, stop_color="#ef4444", stop_opacity=0.1),
            rx.el.svg.stop(offset="1", stop_color="#ef4444", stop_opacity=0.6),
            id="splitColor_" + ticker,
            x1=0,
            y1=0,
            x2=0,
            y2=1,
        )
    )


def stock_vs_peer_chart(data: list[dict], color: str) -> rx.Component:
    return rx.recharts.line_chart(
        rx.recharts.cartesian_grid(
            stroke_dasharray="3 3", vertical=False, stroke="#f3f4f6"
        ),
        rx.recharts.graphing_tooltip(
            content_style={
                "backgroundColor": "rgba(255, 255, 255, 0.96)",
                "borderRadius": "8px",
                "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                "border": "none",
                "fontSize": "11px",
            },
            item_style={"padding": "0"},
            separator="",
        ),
        rx.recharts.x_axis(data_key="Date", hide=True),
        rx.recharts.y_axis(
            hide=False,
            axis_line=False,
            tick_line=False,
            tick={"fontSize": 10, "fill": "#9ca3af"},
            domain=["auto", "auto"],
            width=30,
        ),
        rx.recharts.line(
            data_key="Stock",
            stroke=color,
            stroke_width=2,
            dot=False,
            type_="monotone",
            is_animation_active=False,
        ),
        rx.recharts.line(
            data_key="Peer",
            stroke="#9ca3af",
            stroke_width=2,
            stroke_dasharray="4 4",
            dot=False,
            type_="monotone",
            is_animation_active=False,
        ),
        data=data,
        width="100%",
        height=160,
        margin={"top": 5, "right": 5, "bottom": 5, "left": -20},
    )


def differential_area_chart(
    data: list[dict], ticker: str, offset: float
) -> rx.Component:
    return rx.recharts.area_chart(
        rx.recharts.cartesian_grid(
            stroke_dasharray="3 3", vertical=False, stroke="#f3f4f6"
        ),
        rx.recharts.graphing_tooltip(
            content_style={
                "backgroundColor": "rgba(255, 255, 255, 0.96)",
                "borderRadius": "8px",
                "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                "border": "none",
                "fontSize": "11px",
            },
            item_style={"padding": "0"},
            separator="",
        ),
        define_gradient(ticker, offset),
        rx.recharts.x_axis(data_key="Date", hide=True),
        rx.recharts.y_axis(
            hide=False,
            axis_line=False,
            tick_line=False,
            tick={"fontSize": 10, "fill": "#9ca3af"},
            width=30,
        ),
        rx.recharts.area(
            data_key="Diff",
            stroke="#6b7280",
            stroke_width=1,
            fill="url(#splitColor_" + ticker + ")",
            type_="monotone",
            is_animation_active=False,
        ),
        data=data,
        width="100%",
        height=160,
        margin={"top": 5, "right": 5, "bottom": 5, "left": -20},
    )


def analysis_panel(
    panel: dict[str, str | float | list[dict[str, str | float | None]]],
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    panel["ticker"].to(str),
                    class_name="text-lg font-bold text-gray-900",
                ),
                rx.el.span(
                    panel["current_diff_fmt"].to(str),
                    class_name=rx.cond(
                        panel["current_diff"].to(float) >= 0,
                        "text-xs font-bold px-2 py-1 rounded-full bg-emerald-100 text-emerald-700",
                        "text-xs font-bold px-2 py-1 rounded-full bg-red-100 text-red-700",
                    ),
                ),
                class_name="flex justify-between items-center mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Stock vs Peer Avg",
                        class_name="text-[10px] uppercase font-bold text-gray-400 mb-2 tracking-wider",
                    ),
                    stock_vs_peer_chart(panel["data"].to(list), panel["color"].to(str)),
                    class_name="w-full h-[180px]",
                ),
                rx.el.div(
                    rx.el.p(
                        "Peer Differential (Stock - Peer)",
                        class_name="text-[10px] uppercase font-bold text-gray-400 mb-2 tracking-wider",
                    ),
                    differential_area_chart(
                        panel["data"].to(list),
                        panel["ticker"].to(str),
                        panel["gradient_offset"].to(float),
                    ),
                    class_name="w-full h-[180px]",
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
            ),
            class_name="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow",
        ),
        class_name="w-full",
    )


def relative_strength_grid() -> rx.Component:
    return rx.cond(
        StockState.has_data,
        rx.el.div(
            rx.el.h2(
                "Deep Dive: Relative Strength",
                class_name="text-xl font-bold text-gray-900 mb-4 px-1",
            ),
            rx.el.div(
                rx.foreach(StockState.relative_strength_panels, analysis_panel),
                class_name="grid grid-cols-1 xl:grid-cols-2 gap-6",
            ),
            class_name="w-full max-w-5xl mx-auto mt-8 animate-fade-in pb-12",
        ),
    )