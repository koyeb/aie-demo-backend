from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from core.config import PROMPTER_URL, PROMPTER_API_KEY

class Prompter(object):
    def __init__(self, addr: str, api_key: str):
        self.ai = AsyncOpenAI(
            base_url=addr,
            api_key=api_key,
        )

    async def run(self) -> ChatCompletion:
        return await self.ai.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": [
                            {
                                "type": "text",
                                "text": '''Your job is to create a prompt that I'm going to pass to an image editing model based on the description of the image. 
                                The goal of the prompt is to get the model to replace any written words in the image with the actual items they represent. 
                                For example, if the original image had a woman holding a sign up to their head that says "red curly wig", you would instruct the model to put a red curly wig on the woman.''',
                            },
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": '''Here is a description you've received: 

                                    The image shows a person with long, wavy brown hair. They are wearing a gray hoodie over a white shirt. The person is holding a piece of lined notebook paper above their head with the words "Cowboy Hat" written on it in black ink. The background appears to be an indoor setting, possibly a living room, with a television and some furniture visible. The person is smiling and looking directly at the camera. Create the prompt you will pass to the model to get it to make the edits I want. 

                                    Make it a model-friendly version that often works best for diffusion/image-editing models. Only include the prompt and nothing else.''',
                        },
                    ],
                }
            ],
            model="Qwen/Qwen3-14B",
        )


prompter = Prompter(PROMPTER_URL, PROMPTER_API_KEY)

if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url")
    parser.add_argument("-k", "--api-key")

    args = parser.parse_args()

    d = Prompter(args.url, args.api_key)

    res = asyncio.run(d.run())

    print(res.to_json(indent=4))
