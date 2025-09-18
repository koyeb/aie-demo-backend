from core.config import EMAIL_SMTP, EMAIL_SMTP_USER, EMAIL_SMTP_PASSWORD
import fs
from loguru import logger
from email_lib import render_template, EmailSender
from jinja2 import Environment, FileSystemLoader


class Emailer(object):
    def __init__(self, smtp: str, user: str, password: str):
        self.env = Environment(loader=FileSystemLoader("services/templates"))
        self.email_sender = EmailSender(
            from_email="support@koyeb.com",
            smtp_host=smtp,
            smtp_user=user,
            smtp_pass=password,
        )

    def render(self, name: str, image_url: str) -> str:
        return render_template(
            self.env,
            "email_template.jinja",
            greeting="Hi",
            name=name,
            intro_lines=[
                "Your AI Engineer Paris Koyeb Photobooth results are in!",
                "Here is your custom edited event photo:",
            ],
            action={
                "link": image_url,
                "text": f'<img src="{image_url}" alt="AI edited photo" />',
            },
            tools=[
                {
                    "link": "https://www.koyeb.com/deploy/qwen-2-5-vl-72b-instruct",
                    "text": "Qwen 2.5 VL 72B Instruct",
                },
                {
                    "link": "https://www.koyeb.com/deploy/qwen-3-14b",
                    "text": "Qwen 3 14B",
                },
                {
                    "link": "https://www.koyeb.com/deploy/flux-kontext-dev",
                    "text": "FLUX.1 Kontext [dev]",
                },
                {
                    "link": "https://app.build",
                    "text": "app.build",
                },
            ],
            outro_lines=["Thanks for taking part!"],
            signature="The Koyeb team",
        )

    async def send(self, email: str, name: str, image_url: str):
        success = await self.email_sender.send_email(
            self.render(name, image_url),
            email,
            "Your AI Engineer Paris Koyeb Photobooth results are in!",
            text_type="html",
        )

        if not success:
            raise RuntimeError(f"Failed to send email: {email} ")


emailer = Emailer(EMAIL_SMTP, EMAIL_SMTP_USER, EMAIL_SMTP_PASSWORD)

if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--smtp")
    parser.add_argument("-u", "--smtp-user")
    parser.add_argument("-p", "--smtp-password")
    parser.add_argument("email")
    parser.add_argument("name")
    parser.add_argument("image_url")

    args = parser.parse_args()

    d = Emailer(args.smtp, args.smtp_user, args.smtp_password)

    # print(d.render(args.name, args.image_url))
    asyncio.run(d.send(args.email, args.name, args.image_url))
