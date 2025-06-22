from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='deepseek-r1:1.5b', messages=[
{
'role': 'user',
'content': '帮我分析公司的资本支出：2022年公司资本支出为30万元，2023年公司资本支出为35万元',
},
])
print(response['message']['content'])