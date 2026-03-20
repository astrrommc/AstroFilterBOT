import openai

async def ai(query):
    openai.api_key = "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" 
    response = openai.Completion.create(engine="text-davinci-002", prompt=query, max_tokens=100, n=1, stop=None, temperature=0.9, timeout=5)
    return response.choices[0].text.strip()
     
async def ask_ai(client, m, message):
    try:
        question = message.text.split(" ", 1)[1]
        
        response = await ai(question)
        
        await m.edit(f"{response}")
    except Exception as e:
        
        error_message = f"An error occurred: {e}"
        await m.edit(error_message)
