from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import openai
import os
# Create your views here.
# os.environ['OPENAI_API_KEY'] = 
class GBuilderFile(APIView):

    def post(self, request):
        completion = openai.chat.completions.create( model="gpt-4o",
        messages=[ {"role": "system", "content": "You are a helpful assistant capable of reading coffee cups and fortune telling with it as well"}, 
                    { "role": "user", "content": [
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": request.data['file'][0]
                        }
                        }
                    ] 
                    },
                    { "role": "user", "content": [
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": request.data['file'][1]
                        }
                        }
                    ] 
                    },
                    { "role": "user", "content": [
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": request.data['file'][2]
                        }
                        }
                    ] 
                    },
                   {"role": "user", "content": "بر اساس عکس های داده شده فال قهوه بسیار کامل و طولانی را ایجاد کن و بدون هیچ توضیح و اضافاتی بده"} ] ) 
        print(completion.choices[0].message) 
        return Response(completion.choices[0].message)
