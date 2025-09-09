# Basic AI Moderation placeholder

# In a real application, this would involve more sophisticated NLP models,
# external services (like Google Perspective API, OpenAI Moderation API),
# or custom-trained models.

# For now, a simple keyword-based filter.
INAPPROPRIATE_KEYWORDS = {
    "badword1", "curseword", "offensive_term", "another_bad_word",
    # Add more keywords as needed. Consider variations and misspellings.
    # Be mindful of context; keyword filtering is very naive.
}

# More advanced: consider regular expressions for patterns
# import re
# INAPPROPRIATE_PATTERNS = [
#     re.compile(r"some_regex_pattern", re.IGNORECASE),
# ]

def is_message_inappropriate(message_content: str) -> bool:
    """
    Checks if a message contains inappropriate content based on a keyword list.
    This is a very basic implementation.
    """
    normalized_content = message_content.lower()

    for keyword in INAPPROPRIATE_KEYWORDS:
        if keyword in normalized_content:
            print(f"Moderation: Keyword '{keyword}' found in message.")
            return True

    # Example for regex patterns (if used)
    # for pattern in INAPPROPRIATE_PATTERNS:
    #     if pattern.search(normalized_content):
    #         print(f"Moderation: Pattern '{pattern.pattern}' matched in message.")
    #         return True

    return False

# Example of how a more advanced system might work:
# class ModerationService:
#     def __init__(self, api_key=None):
#         # Initialize connection to an external moderation API or load a model
#         self.api_key = api_key
#         # self.model = load_moderation_model()

#     async def check_message(self, message_content: str) -> dict:
#         """
#         Sends content to a moderation service and returns analysis.
#         Example response: {"is_flagged": True, "categories": ["hate_speech"], "score": 0.9}
#         """
#         # response = await http_client.post("moderation_api_endpoint", json={"text": message_content})
#         # return response.json()
#         pass

# moderation_service = ModerationService(api_key="YOUR_API_KEY")
# async def is_inappropriate_advanced(message_content: str) -> bool:
#     if not message_content.strip():
#         return False
#     try:
#         analysis = await moderation_service.check_message(message_content)
#         if analysis.get("is_flagged", False) and analysis.get("score", 0) > 0.75: # Example threshold
#             return True
#     except Exception as e:
#         print(f"Error calling moderation service: {e}")
#         # Fallback or default behavior: e.g., allow or use basic filter
#         return is_message_inappropriate_basic(message_content) # Fallback to basic
#     return False

# For the current implementation, we'll stick to the simple keyword filter.
# The chat router will use `is_message_inappropriate`.
