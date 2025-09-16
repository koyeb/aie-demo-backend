from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from core.config import PROMPTER_URL, PROMPTER_API_KEY


USER_PROMPT_TEMPLATE = """

Your job is to create a prompt that I'm going to pass to an image editing model
based on the description of the image.

The goal of the prompt is to get the model to replace any item with text on it
with the object described in the text.

For example, if the original image had a woman holding a sign up to their head
that says "red curly wig", you would instruct the model to put a red curly wig
on the woman.

Here is a description you've received:

---
%s
---

Make it a model-friendly version that often works best for diffusion/image-editing models.
Only include the prompt and nothing else.
"""


class Prompter(object):
    def __init__(self, addr: str, api_key: str):
        self.ai = AsyncOpenAI(
            base_url=addr,
            api_key=api_key,
        )

    async def _run(self, description: str) -> ChatCompletion:
        return await self.ai.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": USER_PROMPT_TEMPLATE % description,
                        },
                    ],
                },
            ],
            model="Qwen/Qwen3-14B",
        )

    async def run(self, description: str) -> str:
        result = await self._run(description)
        if (
            not result
            or len(result.choices) == 0
            or not result.choices[0].message.content
        ):
            raise RuntimeError("No result returned")

        return result.choices[0].message.content.lstrip("\n\n")


prompter = Prompter(PROMPTER_URL, PROMPTER_API_KEY)

if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url")
    parser.add_argument("-k", "--api-key")
    parser.add_argument("description")

    args = parser.parse_args()

    d = Prompter(args.url, args.api_key)

    res = asyncio.run(d.run(args.description))

    print(res)
