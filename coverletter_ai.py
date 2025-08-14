#step1 implement a memory unit for AI
# user memory class, def function

from docx import Document
import ollama
from ollama import chat
from ollama import ChatResponse

def read_word_file(file_path):
    """Extracts text from a .docx file"""
    doc = Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return "\n".join(full_text)

class UserMemory:
    def __init__(self):
        #initialize memory
        # user details
        self.resume = read_word_file("C:\\Users\\wengu\Dropbox\\template\\resume_garywen_DS_DE.docx")
        self.senario = read_word_file("C:\\Users\\wengu\\Dropbox\\interview\\Prep_interview.docx")
        self.profile = {}
        # user chat history
        self.history = []
    
    def update_profile(self,cover_letter):
        # update user profile
        self.profile = {
            "zodiac": zodiac,
            "mbti": mbti,
            "gender": gender
        }
    
    # improve memory
    def remember(self, user_input, agent_response):
        self.history.append((user_input,agent_response))
        
   

# step2 call function of LLM
class DeepSeekR1Model:
    # user default LLm deepseek-r1:1.5b, the model could be changed.
    def __init__(self,model_name="deepseek-r1:1.5b"):
        self.model_name = model_name
    # combine zodiac and mbti, analyze the data based on LLM
    def analyze_personality(self,zodiac,mbti):
        prompt = (f"请结合星座“{zodiac}”和MBTI类型：{mbti}”"
                  f"分析该类型人的核心性格特征、情感倾向、适合的职业与成长方向。"
                  f"要求以一个性格、星座分析专家口吻，风格专业、神秘、温柔，同时具有心理学背景，以Astra这个名字自称")


        # role: AI
        # role: user

        response = ollama.chat(model=self.model_name,messages=[{"role":"user","content":prompt}])

        return response['message']['content']
    
# model = DeepSeekR1Model()
# print(model.analyze_personality("天蝎座","infp"))

# Usage example
text_content = read_word_file("C:\\Users\\wengu\Dropbox\\template\\resume_garywen_DS_DE.docx")
print(text_content)