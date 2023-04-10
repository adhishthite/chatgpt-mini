"""
(c) 2023 by Adhish Thite. All rights reserved.
"""
import openai
from rich.markdown import Markdown
from rich.console import Console
from rich.prompt import Prompt
from rich.rule import Rule

# set the API key for the GPT-3 service
openai.api_key = ''

# set the cost to 0
cost: float = 0.0

# Create the Rich console
console = Console()
console.print(Rule("[red][b]ChatGPT Mini[/b][/]\n"))

# Get the model to use. Default is gpt-3.5-turbo
model_id = Prompt.ask("\nModel to use?:\t", choices=[
                      "gpt-4", "gpt-3.5-turbo"], default="gpt-3.5-turbo")

default_context = "General Purpose AI Chatbot"
context = Prompt.ask("\nContext for the chatbot?:\t", default=default_context)

# define a function that generates a response to a conversation
def gpt_conversation(conversation):
    # call the OpenAI API to generate a response to the conversation
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation
    )

    # extract the role and content of the top-ranked response
    conversation.append(
        {
            'role': response.choices[0].message.role,
            'content': response.choices[0].message.content,
        }
    )

    # return the updated conversation
    return conversation, response.usage.total_tokens


# price calculator
def calculate_price_from_tokens(
    total_tokens: int,
    model_id: str = "gpt-3.5-turbo",
    total_price: float = 0.0,
) -> float:
    
    # create a map of model to their price per 1000 tokens
    price_map = {
        "gpt-3.5-turbo": 0.002,
        "gpt-4": 0.03,
    }
    
    # price per 1000 tokens
    price_per_1000 = price_map[model_id]
    
    # calculate the price
    price = (total_tokens / 1000) * price_per_1000
    
    # add the price to the total price
    total_price += price
    
    return round(total_price, 4)
    

# initialize an empty conversation list
conversation = []

# add a system message to the conversation and generate an initial response
conversation.append(
    {
        'role': 'system',
        'content': f"{context}. Respond very precisely. Do not give more information than necessary.",
    }
)
conversation, init_tokens = gpt_conversation(conversation)

# Add to cost
cost += calculate_price_from_tokens(init_tokens, model_id)

# print the last message in the conversation
msg = f"\n\n[blue][i]{conversation[-1]['role'].strip().capitalize()}[/i][/]:\nAI initiated with context\n\n"
console.print(msg)
console.rule(f"[yellow]{model_id}[/]")

# start a loop that waits for user input and generates a response
while True:
    # prompt the user for input
    prompt = console.input('\n[green][i]You:[/i][/]\n')

    if prompt == "exit":
        break
    
    # add the user's message to the conversation
    conversation.append({'role': 'user', 'content': prompt})
    
    # generate a response to the conversation
    conversation, total_tokens = gpt_conversation(conversation)

    # print the last message in the conversation
    role = f"[blue][i]{conversation[-1]['role'].strip().capitalize()}[/i][/]"
    content = f"{conversation[-1]['content'].strip()}"
    
    # Get total tokens and add to cost
    tokens = f"Total tokens: [red]{total_tokens}[/] | Cost: [red]${calculate_price_from_tokens(total_tokens, model_id)}[/]"
    cost += calculate_price_from_tokens(total_tokens, model_id)

    md = f"\n\n{role}:\n{content}\n\n"
    console.print(md)
    console.rule(tokens)
