from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from . import models
import openai
import os
import json

ROOT = "http://10.45.190.255:8000/media/"

# Create your views here.
# os.environ["OPENAI_API_KEY"] = (
# )


class GBuilderFile(APIView):

    def post(self, request):
        data = request.data.get("images")
        file = models.File.objects.create(image=data)
        data = []
        data.append(ROOT + file.image.name)
        print(data)
        completion = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant capable of reading coffee cups and fortune telling with it as well",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data[0]},
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data[0]},
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data[0]},
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": "بر اساس عکس های داده شده فال قهوه بسیار کامل و طولانی را ایجاد کن و بدون هیچ توضیح و اضافاتی بده",
                },
            ],
        )
        print(completion.choices[0].message)
        return Response(completion.choices[0].message)
