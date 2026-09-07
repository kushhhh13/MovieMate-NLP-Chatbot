"""
MovieChatBot: same conversational flow as the notebook (greeting handling,
"show me more", thanks, help, and the main search path), but the retriever
is passed in instead of read from a notebook global, and the final reply
comes from the real LLM generation step in generation.py.
"""

from .intent import parse_intent
from .generation import generate_response


class MovieChatBot:
    def __init__(self, retriever):
        self.retriever = retriever
        self.conversation_history = []
        self.last_results = None

    def chat(self, user_input: str) -> str:
        self.conversation_history.append({"role": "user", "message": user_input})
        user_lower = user_input.lower()

        if any(word in user_lower for word in ["hello", "hi", "hey"]):
            response = (
                "Hello! I'm MovieMate, your personal movie guide. "
                "Ask me anything! For example:\n"
                "- 'Suggest thriller movies after 2000'\n"
                "- 'Best comedy movies from the 1990s'\n"
                "- 'Movies directed by Christopher Nolan'\n"
                "- 'Action movies with rating above 8.5'"
            )

        elif any(word in user_lower for word in ["more", "other", "different", "else"]):
            if self.last_results is not None:
                last_query = None
                for entry in reversed(self.conversation_history):
                    if entry["role"] == "user" and not any(
                        word in entry["message"].lower()
                        for word in ["more", "other", "different", "else", "hello", "hi", "thanks"]
                    ):
                        last_query = entry["message"]
                        break

                if last_query:
                    filters = parse_intent(last_query)
                    results = self.retriever.search(last_query, top_k=10, **filters)
                    results = results.iloc[5:]
                    self.last_results = results
                    response = generate_response(last_query, results)
                else:
                    response = "Could you tell me what kind of movies you're looking for first?"
            else:
                response = "Could you tell me what kind of movies you're looking for first?"

        elif any(word in user_lower for word in ["thank", "thanks", "great", "awesome"]):
            response = "You're welcome! Enjoy your movie! Let me know if you need more recommendations."

        elif "help" in user_lower:
            response = (
                "Here's what you can ask me:\n"
                "- Genre: 'suggest horror movies'\n"
                "- Director: 'movies by Steven Spielberg'\n"
                "- Year: 'crime movies after 2000'\n"
                "- Rating: 'highly rated drama movies'\n"
                "- Runtime: 'comedy movies under 2 hours'\n"
                "- Combined: 'best thriller movies from the 1990s'"
            )

        else:
            filters = parse_intent(user_input)
            results = self.retriever.search(user_input, top_k=5, **filters)
            self.last_results = results
            response = generate_response(user_input, results)

        self.conversation_history.append({"role": "bot", "message": response})
        return response

    def show_history(self):
        for entry in self.conversation_history:
            role = "You" if entry["role"] == "user" else "Bot"
            print(f"{role}: {entry['message']}")
            print("-" * 50)
