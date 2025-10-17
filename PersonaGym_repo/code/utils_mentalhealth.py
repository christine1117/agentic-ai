import time
from openai import OpenAI
from .api_keys import OPENAI_API_KEY



def run_model(
    input_prompt=None,
    persona=None,
    model_card="gpt-4o-mini",  # 預設用便宜的 mini 版
    temperature=0.7,
    top_p=0.9,
    max_tokens=3000,
    message=None,
    system=None,
):

    return openai_chat_gen(
        input_prompt=input_prompt,
        persona=persona,
        model_card=model_card,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        message=message,
        system=system,
    )


def openai_chat_gen(
    input_prompt=None,
    persona=None,
    apikey=OPENAI_API_KEY,
    model_card="gpt-4o-mini",
    temperature=0.7,
    top_p=0.9,
    max_tokens=4000,
    max_attempt=3,
    time_interval=2,
    system=None,
    message=None,
):
   
    client = OpenAI(api_key=apikey)


    if not message:
        if persona:
            persona_prompt = (
                f"You are now adopting the persona of {persona}. "
                "Always speak and reason strictly according to this persona’s mindset, tone, and behavior. "
                "Avoid generic or AI-like language."
            )
            message = [
                {"role": "system", "content": persona_prompt},
                {"role": "user", "content": input_prompt},
            ]
        elif system:
            message = [
                {"role": "system", "content": system},
                {"role": "user", "content": input_prompt},
            ]
        else:
            message = [{"role": "user", "content": input_prompt}]

    for attempt in range(max_attempt):
        try:
            response = client.chat.completions.create(
                model=model_card,
                messages=message,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=0,
                presence_penalty=0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Attempt {attempt + 1}/{max_attempt}] Error: {e}")
            time.sleep(time_interval)

    return "Error: Model failed after multiple attempts."

