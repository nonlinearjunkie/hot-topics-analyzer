from openai import OpenAI

class OpenAIException(Exception):

    def __init__(self):
        super().__init__("Failed to fetch response from OpenAI API.")

class LLM:

    def __init__(self, model_name, model_key):
        self.model_name=model_name
        self.model_key = model_key
        self.openai_client = OpenAI(
            api_key=self.model_key,
            )


    def get_chat_completion(self,prompt):

        messages = [{"role": "user", "content": prompt}]
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0,
            )
        except:
            raise OpenAIException    

        return response.choices[0].message.content    