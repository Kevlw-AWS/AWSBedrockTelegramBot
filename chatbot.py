from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import boto3
import logging
import requests
import io
import base64
from PIL import Image
import random
import string
import subprocess
import json
import os

client = boto3.client('bedrock-runtime')

# Fill in your token here
bot_token = '<CHANGE THIS VALUE>'

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

IMAGE = range(1)

def send_image(botToken, imageFile, chat_id):
        command = 'curl -s -X POST https://api.telegram.org/bot' + botToken + '/sendPhoto -F chat_id=' + str(chat_id) + " -F photo=@" + imageFile
        subprocess.call(command.split(' '))
        return

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    await update.message.reply_text(
        "Hi! What would you like me to create?"
    )

    return IMAGE

async def image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Generates image based on the prompt."""
    user = update.message.from_user
    prompt = update.message.text
    chatid = user.id
    message = 'Creating your image, this will take 30 seconds'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(chatid) + '&parse_mode=Markdown&text=' + message
    requests.get(send_text)
    
    ## Enhance prompt
    prompt = prompt + ", high quality, masterpiece, best quality, full color, highly detailed, cinematic, bright colors, striking, sharp focus, elegant, intricate, artistic, dramatic, epic, 4k, 8k, raw"
    print ('Prompt is ' + prompt)

    negative_prompts = negative_prompts = [
    "poorly rendered",
    "poor background details",
    "poor quality",
    "low quality",
    "lowres",
    "bad anatomy",
    "watermark"
    ]

    style_preset = "photographic"  # (e.g. photographic, digital-art, cinematic, ...)
    clip_guidance_preset = "NONE" # (e.g. FAST_BLUE FAST_GREEN NONE SIMPLE SLOW SLOWER SLOWEST)
    sampler = "K_EULER" # (e.g. DDIM, DDPM, K_DPMPP_SDE, K_DPMPP_2M, K_DPMPP_2S_ANCESTRAL, K_DPM_2, K_DPM_2_ANCESTRAL, K_EULER, K_EULER_ANCESTRAL, K_HEUN, K_LMS)
    width = 1024

    ## generate the image with the API endpoint
    try: 
        request = json.dumps({
        "text_prompts": (
            [{"text": prompt, "weight": 1.0}]
            + [{"text": negprompt, "weight": -1.0} for negprompt in negative_prompts]
        ),
        "cfg_scale": 6,
        "seed": 0,
        "steps": 25,
        # "style_preset": style_preset,
        "clip_guidance_preset": clip_guidance_preset,
        "sampler": sampler,
        "width": width,
        })
        
        ## Change this based on which model you are using
        modelId = "stability.stable-diffusion-xl-v1"

        response = client.invoke_model(body=request, modelId=modelId)
        response_body = json.loads(response.get("body").read())

        print(response_body["result"])
        base_64_img_str = response_body["artifacts"][0].get("base64")
        print(f"{base_64_img_str[0:80]}...")
        image_1 = Image.open(io.BytesIO(base64.decodebytes(bytes(base_64_img_str, "utf-8"))))
        filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        filename = filename + '.png'
        image_1.save(filename)

        ## Send the image
        send_image (bot_token, filename, chatid)

        ## Delete the image
        subprocess.call(['rm', filename])
        await update.message.reply_text(
            "Try typing another prompt!"
        )
        return IMAGE
    
    except:
        print('Error generating image')
        await update.message.reply_text(
            "Error generating image. This may be because the prompt contains filtered words which go against the policy on safe AI use. Please try again."
        )
        return IMAGE


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(bot_token).build()

# Add conversation handler with the states
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
        states={
            IMAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, image),
            ]
        },
        # Will probably not need the /cancel fallback command
        fallbacks=[CommandHandler("start", start)]
    )

# Add commands to the telegram bot
    application.add_handler(conv_handler)

# Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()