import openai
from openai.error import AuthenticationError, InvalidRequestError, RateLimitError

# Constants
PRICE_MAP: dict = {
    "gpt-3.5-turbo": 0.002,
    "gpt-4": 0.06,
}


class ChatGPT:
    def __init__(self, model_id: str, api_key: str, context: str):
        self.model_id = model_id
        self.api_key = api_key
        self.context = context
        self.conversation = []
        self.cost = 0.0

        openai.api_key = api_key

    def add_system_message(self, message: str) -> None:
        self.conversation.append({'role': 'system', 'content': message})

    def add_user_message(self, message: str) -> None:
        self.conversation.append({'role': 'user', 'content': message})

    def gpt_conversation(self) -> dict:
        try:
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

            total_tokens = response.usage.total_tokens
            self.calculate_price_from_tokens(total_tokens)

            return {'status': 'success', 'message': response.choices[0].message.content.strip()}

        except InvalidRequestError as exc:
            return {'status': 'error', 'message': f"Invalid request. Error: {exc}"}
        except RateLimitError as exc:
            return {'status': 'error', 'message': f"Rate limit exceeded. Error: {exc}"}
        except Exception as exc:
            return {'status': 'error', 'message': f"Unexpected error. Error: {exc}"}

    def calculate_price_from_tokens(self, total_tokens: int) -> float:
        price_per_1000 = PRICE_MAP[self.model_id]
        price = (total_tokens / 1000) * price_per_1000
        self.cost += price

        return round(price, 4)
