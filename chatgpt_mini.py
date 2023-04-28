"""
(c) 2023 by Adhish Thite. All rights reserved.
"""

# Import necessary libraries
import os

import openai
from openai.error import AuthenticationError, InvalidRequestError, RateLimitError
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.progress import Progress

# Constants
PRICE_MAP: dict = {
    "gpt-3.5-turbo": 0.002,
    "gpt-4"        : 0.06,
}

# Set your API key and price mapping for different models
try:
    API_KEY: str = os.environ["OPENAI_API_KEY"]
except KeyError:
    print("\n\nPlease set the OPENAI_API_KEY environment variable.\n")
    API_KEY = input("\nEnter the OPENAI_API_KEY Key: ")
    os.environ["OPENAI_API_KEY"] = API_KEY

    if not API_KEY:
        exit(1)

# Set the API key for the OpenAI library
openai.api_key = API_KEY

# Check if the API key is valid
try:
    openai.Model.list()
except AuthenticationError:
    print("\n\nInvalid API Key. Please set the OPENAI_API_KEY environment variable.\n")
    exit(1)


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
        with Progress() as progress:
            task = progress.add_task("[cyan]Waiting for the API response...", total=100)

            try:
                progress.update(task, completed=30)

                response = openai.ChatCompletion.create(
                    model=self.model_id,
                    messages=self.conversation
                )

                progress.update(task, completed=80)
                self.conversation.append(
                    {
                        'role'   : response.choices[0].message.role,
                        'content': response.choices[0].message.content,
                    }
                )

                # Update the progress bar to 100% when the response is received
                progress.update(task, completed=100)

                return response.usage.total_tokens

            except InvalidRequestError as exc:
                console.print("\n\nSeems like there is an error in the request. Do you have access to GPT-3.5 and"
                              " GPT-4?\n")
                console.print(f"This is OpenAI's traceback: [red][b]{exc}[/b][/]\n")
                exit(1)
            except RateLimitError as exc:
                console.print("\n\nSeems like you have exceeded the rate limit for the API. "
                              "Please wait a while before trying again.\n")
                console.print("If you see this error frequently, please view your billing, usage and quotas"
                              "on the OpenAI platform.\n")
                console.print(f"This is OpenAI's traceback: [red][b]{exc}[/b][/]\n")
                exit(1)

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
def get_model_id() -> str:
    return Prompt.ask("\nModel to use?:\t", choices=["gpt-4", "gpt-3.5-turbo"], default="gpt-3.5-turbo")


# Function to get the context from the user
def get_context() -> str:
    # This function prompts the user for a context for the chatbot
    # The default context is "General Purpose AI Chatbot"
    return Prompt.ask("\nContext for the chatbot?:\t", default="General Purpose AI Chatbot")


# Main
console = initialize_console()
model_id = get_model_id()
context = get_context()

# Instantiate the ChatGPT class with the selected model_id and context
chat_gpt = ChatGPT(model_id, context)

# Add a system message to the conversation to set the context and desired response style
chat_gpt.add_system_message(f"{context}. Respond precisely. Do not give more information than necessary.")

# Initialize the conversation with the GPT model and calculate the cost of initial tokens
init_tokens = chat_gpt.gpt_conversation()
chat_gpt.calculate_price_from_tokens(init_tokens)

# Print the initial message from ChatGPT
console.print(f"\n{chat_gpt.get_last_message()}")

# Print a separator rule displaying the chosen model_id
console.rule(f"[yellow]{model_id}[/]")

input_prompt = '\n[green][i]You:[/i][/]\n'

# Main loop to interact with the chatbot
while True:
    # Get user input
    user_input_lines = []
    while True:
        line = console.input(input_prompt)
        if line == "SUBQ":
            break

        user_input_lines.append(line)
        input_prompt = ''  # Remove the "You:" prompt for subsequent lines

    prompt = "\n".join(user_input_lines)

    # Reset the input prompt for the next message
    input_prompt = '\n[green][i]You:[/i][/]\n'

    # If the input is 'exit', break the loop and end the chat
    if prompt == "exit":
        break

    # If the input is 'clear', reset the conversation and display a new initial message
    elif prompt == "clear":
        chat_gpt.conversation = []
        chat_gpt.add_system_message(f"{context}. Respond precisely. Do not give more information than necessary.")
        init_tokens = chat_gpt.gpt_conversation()
        chat_gpt.calculate_price_from_tokens(init_tokens)

        console.print(f"\n{chat_gpt.get_last_message()}")
        console.rule(f"[yellow]{model_id}[/]")

    # For any other input, add the user message and get a response from ChatGPT
    else:
        chat_gpt.add_user_message(prompt)
        total_tokens = chat_gpt.gpt_conversation()
        price = chat_gpt.calculate_price_from_tokens(total_tokens)

        # Calculate the total cost so far
        total_cost = round(chat_gpt.cost, 4)

        # Print the response and a separator rule with token and cost information
        console.print(f"\n{chat_gpt.get_last_message()}")
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
