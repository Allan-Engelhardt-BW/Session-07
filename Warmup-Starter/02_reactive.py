from shiny import App, ui, render, reactive, run_app

app_ui = ui.page_fluid(
    ui.h2("Reactivity 101"),
    ui.input_slider("x", "Value X", 0, 100, 10),
    ui.input_slider("y", "Value Y", 0, 100, 10),
    ui.output_text_verbatim("result"),
    ui.output_text_verbatim("explanation"),
)

def server(input, output, session):
    
    # A Reactive Calculation
    # This only runs when input.x() or input.y() changes.
    # It caches the result.
    @reactive.calc
    def total():
        print("Calculating total...") # Watch the console!
        return input.x() + input.y()

    @render.text
    def result():
        # We call total() like a function
        return f"The sum is: {total()}"

    @render.text
    def explanation():
        # Calling total() again does NOT re-run the print statement
        return f"Double the sum is: {total() * 2}"

app = App(app_ui, server)

# Add this block to run directly
if __name__ == "__main__":
    run_app(app, launch_browser=True)