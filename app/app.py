import reflex as rx
from app.components.config_panel import config_panel
from app.components.performance_chart import performance_chart
from app.components.summary_stats import summary_stats
from app.components.relative_strength import relative_strength_grid
from app.components.data_table import data_table


def index() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.main(
                config_panel(),
                summary_stats(),
                performance_chart(),
                relative_strength_grid(),
                data_table(),
                class_name="container mx-auto px-4 py-12 flex flex-col items-center justify-start min-h-screen",
            ),
            class_name="min-h-screen bg-gray-50 font-['Inter']",
        ),
        class_name="antialiased",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    ],
)
app.add_page(index, route="/")