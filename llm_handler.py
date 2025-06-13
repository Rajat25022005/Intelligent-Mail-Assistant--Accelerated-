import ollama
import json

# This is the robust debugging version of the function
def classify_email_intent_local(email_content):
    """Uses a local LLM to classify the intent of an email."""
    system_prompt = """
    You are an expert email classification system. Analyze the email and classify it
    into one category: meeting_request, information_request, project_update, spam, or other.
    You must also assign a priority: high, medium, or low.
    Return ONLY a valid JSON object with "intent" and "priority" keys.
    """
    try:
        print("--- Attempting to call Ollama for classification... ---")
        response = ollama.chat(
            model='gemma3:4b',  # This should now exist on your machine
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Email content:\n\n{email_content}"},
            ],
            format='json'
        )
        print("--- Call to Ollama succeeded. ---")

        if response and 'message' in response and 'content' in response['message']:
            raw_content = response['message']['content']
            print("--- RAW OLLAMA RESPONSE ---")
            print(raw_content)
            print("---------------------------")

            return json.loads(raw_content)
        else:
            print("!!! ERROR: Ollama response was empty or malformed. !!!")
            print("Full Response Object:", response)
            return None

    except Exception as e:
        print(f"!!! An exception occurred during the classification process: {e} !!!")
        return None

# This is your original function, include it as well
def generate_reply_local(email_content, intent, context=None):
    """
    Uses Gemma 2 to generate a context-aware reply.
    Dynamically adjusts its prompt based on the provided context.
    """
    base_prompt = f"""
    You are a helpful email assistant. Your task is to draft a polite, professional, and concise reply 
    to the following email. The email has been classified with the intent: '{intent}'.
    """

    if context:
        context_prompt = f"""
        To help you draft the reply, please use the following context:
        --- CONTEXT ---
        {context}
        --- END CONTEXT ---
        Based on the email and the provided context, draft a suitable response.
        """
        system_prompt = base_prompt + context_prompt
    else:
        system_prompt = base_prompt + "\nDraft a relevant and helpful reply based on the intent."

    system_prompt += "\n\nDo not include a subject line. Only provide the body of the reply."

    try:
        response = ollama.chat(
            model='gemma3:4b',  # Or your preferred model for generation
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Here is the original email:\n\n{email_content}"},
            ]
        )
        return response['message']['content']
    except Exception as e:
        print(f"An error occurred while generating reply: {e}")
        return None