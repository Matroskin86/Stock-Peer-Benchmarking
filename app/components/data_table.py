import reflex as rx
from app.states.stock_state import StockState


def table_header_cell(col: str) -> rx.Component:
    return rx.el.th(
        rx.el.div(
            rx.el.span(col),
            rx.cond(
                StockState.table_sort_column == col,
                rx.icon(
                    rx.cond(StockState.table_sort_asc, "arrow-up", "arrow-down"),
                    size=14,
                    class_name="text-violet-600",
                ),
                rx.icon(
                    "arrow-up-down",
                    size=14,
                    class_name="text-gray-300 opacity-0 group-hover:opacity-100",
                ),
            ),
            class_name="flex items-center gap-2 group cursor-pointer",
        ),
        on_click=lambda: StockState.sort_table(col),
        class_name="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider select-none hover:bg-gray-50 transition-colors",
    )


def table_row(row: dict) -> rx.Component:
    return rx.el.tr(
        rx.foreach(
            StockState.table_columns,
            lambda col: rx.el.td(
                rx.cond(
                    col == "Date",
                    rx.el.span(
                        row[col].to(str), class_name="font-medium text-gray-900"
                    ),
                    rx.el.span(
                        row[col].to(float).to_string(),
                        class_name="text-gray-600 font-mono",
                    ),
                ),
                class_name="px-6 py-4 whitespace-nowrap text-sm border-b border-gray-100",
            ),
        ),
        class_name="hover:bg-gray-50 transition-colors",
    )


def data_table() -> rx.Component:
    return rx.cond(
        StockState.has_data,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Raw Market Data", class_name="text-xl font-bold text-gray-900"
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.icon("download", size=16),
                            "Export CSV",
                            on_click=StockState.download_csv,
                            class_name="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors shadow-sm",
                        ),
                        rx.el.button(
                            rx.cond(
                                StockState.is_fullscreen,
                                rx.icon("minimize", size=16),
                                rx.icon("maximize", size=16),
                            ),
                            on_click=StockState.toggle_fullscreen,
                            class_name="p-1.5 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors",
                            title="Toggle Fullscreen",
                        ),
                        class_name="flex items-center gap-2",
                    ),
                    class_name="flex justify-between items-center mb-4",
                ),
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.foreach(StockState.table_columns, table_header_cell),
                                class_name="bg-gray-50 border-b border-gray-200",
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(StockState.paginated_table_data, table_row),
                            class_name="bg-white divide-y divide-gray-100",
                        ),
                        class_name="min-w-full divide-y divide-gray-200",
                    ),
                    class_name="overflow-x-auto border border-gray-200 rounded-xl shadow-sm bg-white",
                ),
                rx.el.div(
                    rx.el.p(
                        f"Page ",
                        rx.el.span(StockState.table_page, class_name="font-semibold"),
                        " of ",
                        rx.el.span(
                            StockState.table_total_pages, class_name="font-semibold"
                        ),
                        class_name="text-sm text-gray-600",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Previous",
                            on_click=lambda: StockState.set_table_page(
                                StockState.table_page - 1
                            ),
                            disabled=StockState.table_page <= 1,
                            class_name="px-3 py-1.5 text-sm font-medium border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed bg-white transition-colors",
                        ),
                        rx.el.button(
                            "Next",
                            on_click=lambda: StockState.set_table_page(
                                StockState.table_page + 1
                            ),
                            disabled=StockState.table_page
                            >= StockState.table_total_pages,
                            class_name="px-3 py-1.5 text-sm font-medium border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed bg-white transition-colors",
                        ),
                        class_name="flex gap-2",
                    ),
                    class_name="flex justify-between items-center mt-4",
                ),
                class_name="w-full h-full flex flex-col",
            ),
            class_name=rx.cond(
                StockState.is_fullscreen,
                "fixed inset-0 z-50 bg-gray-50 p-6 overflow-auto animate-fade-in",
                "w-full max-w-5xl mx-auto mt-8 mb-12 animate-fade-in bg-white p-6 rounded-2xl border border-gray-200 shadow-sm",
            ),
        ),
    )