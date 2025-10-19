import openai
import asyncio


class Chatgpt_json:
    def __init__(self):
        self.client = None

    @classmethod
    async def create(cls, openai_key):
        instance = cls()
        await instance.async_init(openai_key)
        return instance

    async def async_init(self, openai_key):
        self.client = openai.AsyncOpenAI(base_url="https://api.rcouyi.com/v1", api_key=openai_key)

    async def process_message(self, message: list):
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=message,
                    response_format={"type": "json_object"},
                ),
                timeout=360  # Timeout in seconds
            )
            print(response)
            return response
        except asyncio.TimeoutError:
            print("Request timed out")
        except Exception as e:
            print(f"An error occurred: {e}")


class Chatgpt_image:
    def __init__(self):
        self.client = None

    @classmethod
    async def create(cls, openai_key):
        instance = cls()
        await instance.async_init(openai_key)
        return instance

    async def async_init(self, openai_key):
        self.client = openai.AsyncOpenAI(base_url="https://api.rcouyi.com/v1", api_key=openai_key)

    async def generate(self, message: str):
        try:
            response = await asyncio.wait_for(
                self.client.images.generate(
                    model="dall-e-3",
                    size="1024x1024",
                    prompt=message,
                    quality="standard",
                    n=1,
                ),
                timeout=360
            )
            return response
        except asyncio.TimeoutError:
            print("Request timed out")
        except Exception as e:
            print(f"An error occurred: {e}")


