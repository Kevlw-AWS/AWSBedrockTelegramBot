# README
## TXT2IMG Generative AI Telegram Chatbot
 
## What is this?
This repository contains code for a Telegram chatbot that receives a text prompt, adds additional words to enhance the prompt and then sends the prompt to Amazon Bedrock to generate an image before sending the image back to the user. Images are deleted after they are sent.

The chatbot runs in a docker container and is meant to be deployed on ECS Fargate. Deploying this on AWS and using Amazon Bedrock will incur costs. You can find more information on ECS pricing [here](https://aws.amazon.com/ecs/pricing/) and on Bedrock pricing [here](https://aws.amazon.com/bedrock/pricing/). 

## Prerequisites
1. An AWS account.
2. A way to build the container - either Docker running on your local machine or CodeBuild on AWS. 
3. An [Amazon ECR](https://aws.amazon.com/ecr/) repository on AWS. 
4. Allow listing of the relevant generative AI model in Amazon Bedrock. Documentation on setting up Bedrock can be found [here](https://docs.aws.amazon.com/bedrock/latest/userguide/setting-up.html).
5. A Telegram chatbot and the API key. Instructions on creating a chatbot with BotFather can be found [here](https://www.freecodecamp.org/news/how-to-create-a-telegram-bot-using-python/).

## Deployment Instructions
You will need an AWS account to follow these instructions. 

1. Copy the repository.
2. Add your Telegram bot API key to the `bot_token` variable in the `chatbot.py` file. 
3. Change the `modelId` variable to the model that you plan to use.
4. Build the container and [push it to ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html).
5. Create an IAM task role with the right permissions. You will minimally need the `bedrock:InvokeModel` permission to invoke the Bedrock API and permissions for the application to write to CloudWatch Logs so that you can view the logs from the chatbot.
6. [Deploy the container onto ECS Fargate in a public subnet](https://aws.plainenglish.io/deploying-a-docker-container-in-aws-using-fargate-5a19a140b018). The Telegram Chatbot is lightweight and only requires a small amount of CPU and memory. 0.25 vCPU and the smallest amount of memory you can assign it should work. 
7. In a few moments the task should be marked as deployed and your chatbot should be working.

## Additional Resources
* [amazon-bedrock-workshop](https://github.com/aws-samples/amazon-bedrock-workshop)
* If you want to host your own StableDiffusion server, you can refer to my other repo [here](https://github.com/Kevlw-AWS/stable-diffusion-telegram-bot)
