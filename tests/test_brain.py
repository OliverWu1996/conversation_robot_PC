"""Tests for robot.brain — conversation processing and learning."""

import pytest
from unittest.mock import MagicMock, call
from robot.brain import Brain


@pytest.fixture
def brain():
    memory = MagicMock()
    memory.recall_facts.return_value = []
    life = MagicMock()
    life.mood = "happy"
    life.get_status.return_value = {
        "mood": "happy",
        "energy": 90.0,
        "happiness": 70.0,
        "curiosity": 60.0,
        "age_days": 3,
        "interactions_today": 2,
    }
    return Brain(memory=memory, life=life)


# ------------------------------------------------------------------
# Basic responses
# ------------------------------------------------------------------


def test_greeting_returns_nonempty_response(brain):
    response = brain.process("Hello!")
    assert response and isinstance(response, str)


def test_farewell_returns_nonempty_response(brain):
    response = brain.process("Goodbye!")
    assert response and isinstance(response, str)


def test_how_are_you_includes_mood(brain):
    brain.life.mood = "curious"
    response = brain.process("How are you?")
    assert "curious" in response


def test_status_query_returns_info(brain):
    response = brain.process("What is your status?")
    assert "happy" in response.lower() or "energy" in response.lower()


def test_default_response_for_unknown_input(brain):
    response = brain.process("Something completely random and unrecognised 12345")
    assert response and isinstance(response, str)


# ------------------------------------------------------------------
# Teaching / learning
# ------------------------------------------------------------------


def test_teach_stores_fact_in_memory(brain):
    brain.process("Remember that the sky is blue")
    brain.memory.learn_fact.assert_called_once_with("user_taught", "the sky is blue")


def test_learn_that_pattern(brain):
    brain.process("Learn that water boils at 100 degrees")
    brain.memory.learn_fact.assert_called_once_with("user_taught", "water boils at 100 degrees")


# ------------------------------------------------------------------
# Recall
# ------------------------------------------------------------------


def test_recall_known_topic(brain):
    brain.memory.recall_facts.return_value = [("Python is great", 1.0)]
    response = brain.process("What do you know about Python?")
    assert "Python" in response
    assert "Python is great" in response


def test_recall_unknown_topic(brain):
    brain.memory.recall_facts.return_value = []
    response = brain.process("Tell me about quantum computing")
    assert "quantum computing" in response.lower()


# ------------------------------------------------------------------
# Side-effects: memory and life updated
# ------------------------------------------------------------------


def test_process_stores_conversation(brain):
    brain.process("Hello!")
    brain.memory.store_conversation.assert_called_once()
    args = brain.memory.store_conversation.call_args[0]
    assert args[0] == "Hello!"


def test_process_triggers_life_interaction(brain):
    brain.process("Hello!")
    brain.life.on_interaction.assert_called_once()


# ------------------------------------------------------------------
# Edge cases
# ------------------------------------------------------------------


def test_empty_input_returns_prompt(brain):
    response = brain.process("")
    assert response


def test_whitespace_only_input_returns_prompt(brain):
    response = brain.process("   ")
    assert response


# ------------------------------------------------------------------
# Sentiment estimation
# ------------------------------------------------------------------


def test_positive_sentiment_score(brain):
    score = brain._estimate_sentiment("I love this, it's great and wonderful")
    assert score > 0


def test_negative_sentiment_score(brain):
    score = brain._estimate_sentiment("This is terrible and awful")
    assert score < 0


def test_neutral_sentiment_score(brain):
    score = brain._estimate_sentiment("The weather is okay today")
    assert score == 0.0
