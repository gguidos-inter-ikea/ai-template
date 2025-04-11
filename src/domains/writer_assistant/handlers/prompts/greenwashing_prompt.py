def create_greenwashing_prompt(self, latest_response):
        Default_system_prompt = "Role: You are a helpful assistant to the user.\
            \nText Style: Friendly and helpful.\
            \nMood of the text: Positive and encouraging.\
            \nThe Audience of the text: The user.\
            \nKind of text: Chat.\
            \nPurpose of the text: To provide helpful information to the user."
        Content_prompt = "Following the instructions above analyze the latest response for greenwashing\
            and give a detailed analyses and suggestions how to improve the text to avoid greenwashing"
        prompt_text = latest_response
        return Default_system_prompt, Content_prompt, prompt_text