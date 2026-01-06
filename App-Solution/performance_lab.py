from shiny import App, render, ui, reactive
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

app_ui = ui.page_fluid(
    ui.h2("The Fast App 🐇"),
    ui.input_slider("n", "Sample Size", 100, 1000, 100),
    ui.input_action_button("submit", "Run Query", class_="btn-primary"),
    ui.output_text_verbatim("info"),
    ui.output_plot("plot")
)

def server(input, output, session):

    # @reactive.calc caches the result!
    # It only re-runs if its inputs change.
    @reactive.calc
    def get_data_cached():
        # DEBOUNCE PATTERN (Manual)
        # We take a dependency on the button, not the slider directly.
        input.submit()
        
        # We use isolate() to read the slider value without taking a dependency on it.
        # This means moving the slider DOES NOT trigger this function.
        # Only clicking the button triggers it.
        with reactive.isolate():
            n = input.n()

        print("Querying Database... (Optimized)")
        time.sleep(1.0) 
        return pd.DataFrame({'x': range(n), 'y': np.random.randn(n)})

    @render.text
    def info():
        # Calls the cached function. If it's already run for this 'n', it returns instantly.
        df = get_data_cached()
        return f"Loaded {len(df)} rows from the database."

    @render.plot
    def plot():
        # Calls the cached function. No double query!
        df = get_data_cached()
        fig, ax = plt.subplots()
        ax.plot(df['x'], df['y'])
        return fig

app = App(app_ui, server)
