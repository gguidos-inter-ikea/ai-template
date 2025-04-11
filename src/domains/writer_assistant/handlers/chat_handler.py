import logging
logger = logging.getLogger(__name__)

class ChatHandler:
    """
    Handles chat interactions with the OpenAI API.
    """

    def max_tokens(self, max_char_length: int = None) -> int:
        """
        Generates a response from the OpenAI API based on the chat history.
        """
        if max_char_length is not None:
            max_tokens = round(max_char_length / 4)
            logger.info(f"max_char_length: {max_char_length}, max_tokens: {max_tokens}")  
        else:
            max_tokens = None

        return max_tokens
    
    async def send_prompt_to_llm(
            self,
            request,
            Default_system_prompt,
            content_prompt,
            max_tokens,
            chat_history,
            model
    )-> dict:
        openai_client = request.app.state.ai_model_client

        logger.info("generating llm response using model: {model}".format(model=model))
        latest_chat_history = chat_history
        if latest_chat_history == []:
            chat_history_string = ""
        else:
            latest_chat_history = [f"USER: {msg['prompt']}\nLLM: {msg['generated_text']}" for msg in chat_history]
            chat_history_string = "\n".join(latest_chat_history)

        llm_messages= [
                {"role": "system", "content": Default_system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": chat_history_string},
                    {"type": "text", "text": content_prompt}
                ]}
        ],
        response = openai_client.chat.completions.create(
            model=model,
            messages=llm_messages,
            temperature=0.1,
            max_tokens=max_tokens,
        )
        if response.choices[0].finish_reason == "stop":
            text = response.choices[0].message.content

            return text
        else:
            print("error code: ", response.choices[0].finish_reason)
            return f"The response was not completed due to {response.choices[0].finish_reason} issues. Try again, please."
        
    def add_chat_to_history(self, latest_response, chat_history):
        """
        Adds a chat message to the history.

        Args:
            role (str): The role of the sender (user or assistant).
            content (str): The content of the message.
        """