import json


def parse_json_response(response):
    print("=======Entering parser============")

    #print("\n========== RAW RESPONSE ==========")
    #print(type(response))
    #print(response)
    #print("=================================\n")

    content = response.content

    #print("\n========== RAW CONTENT ==========")
    #print(type(content))
    #print(content)
    #print("=================================\n")

    # OpenAI / Anthropic
    if isinstance(content, str):
        text = content

    # Gemini
    elif isinstance(content, list):
        text = ""

        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                text += part.get("text", "")

    else:
        raise Exception(f"Unsupported response type: {type(content)}")

    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1)

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    print("\n========== FILTERED ==========")
    print(text)
    print("============= Exiting Parser=================\n")

    return json.loads(text)