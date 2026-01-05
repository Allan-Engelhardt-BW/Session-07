from shiny import App, ui, render, run_app

app_ui = ui.page_fluid(
    ui.h2("Widget Showcase"),
    ui.row(
        ui.column(4, 
            ui.input_select("class", "Business Class", 
                          choices=["Property", "Motor", "Casualty"]),
            ui.input_date("val_date", "Valuation Date"),
            ui.input_numeric("threshold", "Large Loss Threshold", 100000),
            ui.input_switch("gross", "Show Gross?", True),
        ),
        ui.column(8,
            ui.output_text_verbatim("summary")
        )
    )
)

def server(input, output, session):
    @render.text
    def summary():
        return f"""
        Selected Class: {input.class_()}
        Date: {input.val_date()}
        Threshold: {input.threshold()}
        Gross: {input.gross()}
        """

app = App(app_ui, server)

# Add this block to run directly
if __name__ == "__main__":
    run_app(app, launch_browser=True)