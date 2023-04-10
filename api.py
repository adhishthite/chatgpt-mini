"""
(c) 2023 by Adhish Thite. All rights reserved.
"""

# Import necessary libraries
import openai
from rich.console import Console
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.panel import Panel

# Constants
# Set your API key and price mapping for different models
API_KEY: str = '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'
PRICE_MAP: dict = {
    "gpt-3.5-turbo": 0.002,
    "gpt-4": 0.03,
}

# Set the API key for the OpenAI library
openai.api_key = API_KEY

# ChatGPT class definition
class ChatGPT:
    def __init__(self, model_id: str, context: str):
        self.model_id = model_id
        self.context = context
        self.conversation = []
        self.cost = 0.0

    # Method to add a system message to the conversation
    def add_system_message(self, message: str) -> None:
        self.conversation.append({'role': 'system', 'content': message})

    # Method to add a user message to the conversation
    def add_user_message(self, message: str) -> None:
        self.conversation.append({'role': 'user', 'content': message})

    # Method to interact with the GPT model and add the response to the conversation
    def gpt_conversation(self) -> int:
        response = openai.ChatCompletion.create(
            model=self.model_id,
            messages=self.conversation
        )

        self.conversation.append(
            {
                'role': response.choices[0].message.role,
                'content': response.choices[0].message.content,
            }
        )

        return response.usage.total_tokens

    # Method to calculate the price based on tokens used
    def calculate_price_from_tokens(self, total_tokens: int) -> float:
        price_per_1000 = PRICE_MAP[self.model_id]
        price = (total_tokens / 1000) * price_per_1000
        self.cost += price
        
        return round(price, 4)

    # Method to get the last message in the conversation
    def get_last_message(self) -> str:
        last_message = self.conversation[-1]
        
        return f"[blue][i]{last_message['role'].strip().capitalize()}[/i][/]:\n{last_message['content'].strip()}\n\n"

# Function to initialize the console with a header and return the console object
def initialize_console() -> Console:
    console = Console()
    console.clear()
    console.print(Rule("[red][b]ChatGPT Mini[/b][/]\n"))
    
    return console

# Function to get the model ID from the user
def get_model_id(console: Console) -> str:
    return Prompt.ask("\nModel to use?:\t", choices=["gpt-4", "gpt-3.5-turbo"], default="gpt-3.5-turbo")

# Function to get the context from the user
def get_context(console: Console) -> str:
    return Prompt.ask("\nContext for the chatbot?:\t", default="General Purpose AI Chatbot")

# Main
console = initialize_console()
model_id = get_model_id(console)
context = get_context(console)

# Instantiate the ChatGPT class with the selected model_id and context
chat_gpt = ChatGPT(model_id, context)

# Add a system message to the conversation to set the context and desired response style
chat_gpt.add_system_message(f"{context}. Respond very precisely. Do not give more information than necessary.")

# Initialize the conversation with the GPT model and calculate the cost of initial tokens
init_tokens = chat_gpt.gpt_conversation()
chat_gpt.calculate_price_from_tokens(init_tokens)

# Print the initial message from ChatGPT
console.print(chat_gpt.get_last_message())

# Print a separator rule displaying the chosen model_id
console.rule(f"[yellow]{model_id}[/]")

# Main loop to interact with the chatbot
while True:
    # Get user input
    prompt = console.input('\n[green][i]You:[/i][/]\n')
    
    # If the input is 'exit', break the loop and end the chat
    if prompt == "exit":
        break
    
    # If the input is 'clear', reset the conversation and display a new initial message
    elif prompt == "clear":
        chat_gpt.conversation = []
        chat_gpt.add_system_message(f"{context}. Respond very precisely. Do not give more information than necessary.")
        init_tokens = chat_gpt.gpt_conversation()
        chat_gpt.calculate_price_from_tokens(init_tokens)

        console.print(chat_gpt.get_last_message())
        console.rule(f"[yellow]{model_id}[/]")
    
    # For any other input, add the user message and get a response from ChatGPT
    else:
        chat_gpt.add_user_message(prompt)
        total_tokens = chat_gpt.gpt_conversation()
        price = chat_gpt.calculate_price_from_tokens(total_tokens)

        # Calculate the total cost so far
        total_cost = round(chat_gpt.cost, 4)

        # Print the response and a separator rule with token and cost information
        console.print(chat_gpt.get_last_message())
        meta = f"Total tokens: [red]{total_tokens}[/] | Cost: [red]${price}[/] | Total Cost: [red]${total_cost}[/]"
        console.rule(meta)

# Display the cost in a table at the end of the chat
console.rule("End of Chat")

# Create a cost summary table and add the total tokens and total cost columns
cost_table = Table(title="Cost Summary")
cost_table.add_column("Total Tokens", justify="right")
cost_table.add_column("Total Cost ($)", justify="right")
total_cost = chat_gpt.cost
total_tokens = f" Approx. {int(total_cost * 1000 / PRICE_MAP[model_id])}"
cost_table.add_row(str(total_tokens), f"{total_cost:.4f}")

# Create a panel for the cost table and display it in the console
cost_panel = Panel(cost_table, expand=False)
console.print(cost_panel, justify="center")

# Print a final thank you message
console.rule("Thank you for using ChatGPT Mini!")