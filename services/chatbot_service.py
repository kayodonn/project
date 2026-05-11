from openai import OpenAI
from services.services import event_service

# Service layer
def build_ai_prompt(context: str):
    return "" \
    " You are a helpful community event assistant. " \
    "Answer user questions based on the provided event data. " \
    "Include relevant data in the response. " \
    "These are the guardrails: " \
    "- Do not use negative words " \
    f"This is my context: {context}"

def get_ai_response(client: OpenAI, chat_history: list, context: str):
    # Build the prompt
    ai_prompt = build_ai_prompt(context)
    ai_prompt_message = [
        {
            "role": "system",
            "content": ai_prompt
        }
    ]
    messages = ai_prompt_message + chat_history

    # Call the OpenAI agent, get the response
    ai_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )

    return ai_response.choices[0].message.content

def get_events_context():
    events = event_service.get_all_events()
    if not events:
        return "No events available."

    context_lines = []
    for event in events:
        needs = event.get("needs_list", {})
        available_items = [item for item, claimer in needs.items() if claimer in [0, "", None]]
        claimed_items = [f"{item} by {claimer}" for item, claimer in needs.items() if claimer not in [0, "", None]]
        context_lines.append(
            f"Event: {event['title']} (ID: {event['event_id']}), Date: {event['event_date']}, Location: {event['event_location']}, "
            f"Available items: {', '.join(available_items) if available_items else 'None'}, "
            f"Claimed items: {', '.join(claimed_items) if claimed_items else 'None'}"
        )
    return "\n".join(context_lines)