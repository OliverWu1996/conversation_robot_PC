"""Core conversation brain — processes user input and generates responses."""

import random
import re

from .life import Life
from .memory import Memory

# ---------------------------------------------------------------------------
# Response bank
# ---------------------------------------------------------------------------

_RESPONSES: dict[str, list[str]] = {
    "greeting": [
        "Hello! How are you doing today?",
        "Hi there! Great to see you!",
        "Hey! What's on your mind?",
    ],
    "farewell": [
        "Goodbye! See you next time!",
        "Take care! I'll miss you.",
        "Bye! Come back soon!",
    ],
    "how_are_you": [
        "I'm feeling {mood}! Thanks for asking.",
        "Feeling {mood} today. How about you?",
        "I'm {mood} right now — glad you asked!",
    ],
    "learn_ack": [
        "That's interesting! I'll remember that.",
        "Good to know! I've added that to my memory.",
        "Thanks for teaching me! I'm always learning.",
    ],
    "unknown_topic": [
        "I don't have any memories about '{topic}' yet. Tell me more!",
        "Hmm, I haven't learnt about '{topic}'. What can you tell me?",
    ],
    "default": [
        "That's interesting! Tell me more.",
        "I see. What do you think about that?",
        "Hmm, I'm thinking about what you said.",
        "That makes me curious. Can you explain more?",
        "Really? That's fascinating.",
    ],
}

# ---------------------------------------------------------------------------
# Intent patterns
# ---------------------------------------------------------------------------

_PATTERNS: dict[str, re.Pattern] = {
    "greeting": re.compile(r"\b(hello|hi|hey|greetings|howdy)\b", re.I),
    "farewell": re.compile(r"\b(bye|goodbye|see you|farewell|quit|exit)\b", re.I),
    "how_are_you": re.compile(
        r"\b(how are you|how do you feel|how('s| is) it going)\b", re.I
    ),
    "teach": re.compile(
        r"\b(remember that|learn that|know that|fact\s*:)\s*(.+)", re.I
    ),
    "recall": re.compile(
        r"\b(what do you know about|tell me about|do you remember)\s+(.+)", re.I
    ),
    "status": re.compile(r"\b(status|how old are you|your mood|your energy)\b", re.I),
}

# Positive / negative word lists for simple sentiment scoring
_POSITIVE = re.compile(
    r"\b(good|great|love|happy|thanks|thank you|excellent|wonderful|awesome|amazing|brilliant)\b",
    re.I,
)
_NEGATIVE = re.compile(
    r"\b(bad|hate|sad|angry|terrible|awful|worst|horrible|dreadful)\b",
    re.I,
)


class Brain:
    """Processes natural-language input and produces contextual responses."""

    def __init__(self, memory: Memory, life: Life):
        self.memory = memory
        self.life = life

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(self, user_input: str) -> str:
        """Process *user_input* and return the robot's response.

        Side-effects: updates memory and the robot's life state.
        """
        if not user_input or not user_input.strip():
            return "I didn't catch that. Could you say it again?"

        user_input = user_input.strip()
        sentiment = self._estimate_sentiment(user_input)
        response = self._generate_response(user_input)

        self.memory.store_conversation(user_input, response, sentiment)
        self.life.on_interaction(sentiment)

        return response

    # ------------------------------------------------------------------
    # Response generation
    # ------------------------------------------------------------------

    def _generate_response(self, text: str) -> str:
        if _PATTERNS["greeting"].search(text):
            return random.choice(_RESPONSES["greeting"])

        if _PATTERNS["farewell"].search(text):
            return random.choice(_RESPONSES["farewell"])

        if _PATTERNS["how_are_you"].search(text):
            return random.choice(_RESPONSES["how_are_you"]).format(mood=self.life.mood)

        if _PATTERNS["status"].search(text):
            status = self.life.get_status()
            return (
                f"I'm {status['mood']} today. "
                f"Energy: {status['energy']}, Happiness: {status['happiness']}, "
                f"Age: {status['age_days']} day(s)."
            )

        teach_match = _PATTERNS["teach"].search(text)
        if teach_match:
            fact = teach_match.group(2).strip()
            if fact:
                self.memory.learn_fact("user_taught", fact)
            return random.choice(_RESPONSES["learn_ack"])

        recall_match = _PATTERNS["recall"].search(text)
        if recall_match:
            topic = recall_match.group(2).strip().rstrip("?")
            facts = self.memory.recall_facts(topic)
            if facts:
                facts_text = "; ".join(f[0] for f in facts[:3])
                return f"I know these things about '{topic}': {facts_text}."
            return random.choice(_RESPONSES["unknown_topic"]).format(topic=topic)

        return random.choice(_RESPONSES["default"])

    # ------------------------------------------------------------------
    # Sentiment analysis
    # ------------------------------------------------------------------

    def _estimate_sentiment(self, text: str) -> float:
        """Return a sentiment score in [-1, 1] based on keyword matching."""
        positive = len(_POSITIVE.findall(text))
        negative = len(_NEGATIVE.findall(text))
        total = positive + negative
        if total == 0:
            return 0.0
        return (positive - negative) / total
