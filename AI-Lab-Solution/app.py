from shiny import App, ui, render, reactive
import polars as pl
from openai import OpenAI
import json

# Load Data
df = pl.read_csv("properties.csv")

import os

# Configuration
# Choose provider: 'ollama', 'gemini', or 'azure'
PROVIDER = 'ollama' 

# --- Client Setup ---
if PROVIDER == 'ollama':
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama', # required but unused
    )
    MODEL = "llama3.2:3b"

elif PROVIDER == 'gemini':
    # Requires: GOOGLE_API_KEY environment variable or set directly
    # Usage: export GOOGLE_API_KEY="AIza..."
    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.environ.get("GOOGLE_API_KEY", "INSERT_KEY_HERE"),
    )
    MODEL = "gemini-1.5-flash"

elif PROVIDER == 'azure':
    # Requires: AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT
    from openai import AzureOpenAI
    client = AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY", "INSERT_KEY_HERE"),
        api_version="2023-12-01-preview",
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/")
    )
    MODEL = "gpt-4o" # or your deployment name


SYSTEM_PROMPT = """
You are a data filtering assistant. 
The user will ask for properties based on specific criteria.
You must return a JSON object representing the filters.
Do not return any text other than the JSON.

The dataset has the following columns and values:
- Location: London, Manchester, Birmingham, Leeds, Glasgow, Bristol
- Construction: Masonry, Timber Frame, Steel Frame, Reinforced Concrete
- FloodRisk: Low, Medium, High, Very High
- SumInsured: (Numeric)
- YearBuilt: (Numeric)

Example User Input: "Show me high risk timber buildings in London"
Example JSON Output: {"FloodRisk": "High", "Construction": "Timber Frame", "Location": "London"}

If the user asks to reset or show all, return an empty JSON object: {}
"""

app_ui = ui.page_fluid(
    ui.h2("AI Property Filter"),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.chat_ui("chat"),
            width=400
        ),
        ui.card(
            ui.card_header("Property Schedule"),
            ui.output_data_frame("grid"),
        )
    )
)

def server(input, output, session):
    
    filtered_df = reactive.Value(df)
    
    chat = ui.Chat(id="chat", messages=[
        # FIXED
        {"role": "assistant", "content": "Describe the properties you want to see (eg 'High risk timber in Glasgow')."}
    ])
    
    @chat.on_user_submit
    async def handle_query(user_input: str):
        # 1. Append user message
        await chat.append_message(user_input)
        
        # 2. Call LLM
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            json_str = response.choices[0].message.content
            filters = json.loads(json_str)
            
            # 3. Apply Filters
            current_df = df
            filter_desc = []
            
            if not filters:
                filter_desc.append("Showing all data.")
            else:
                for col, val in filters.items():
                    if col in df.columns:
                        # Simple equality check for strings
                        # For numeric, you'd need more complex logic (>, <) which requires a smarter prompt
                        current_df = current_df.filter(pl.col(col) == val)
                        filter_desc.append(f"{col}='{val}'")
            
            filtered_df.set(current_df)
            
            # 4. Respond to user
            msg = f"Applied filters: {', '.join(filter_desc)}" if filter_desc else "Reset filters."
            await chat.append_message(msg)
            
        except Exception as e:
            await chat.append_message(f"Error: {str(e)}")

    @render.data_frame
    def grid():
        return render.DataGrid(filtered_df())

app = App(app_ui, server)

if __name__ == "__main__":
    run_app(app, launch_browser=True)