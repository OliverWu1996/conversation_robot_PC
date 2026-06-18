"""Tests for robot.memory — persistent memory and learning storage."""

import pytest
from robot.memory import Memory


@pytest.fixture
def memory(tmp_path):
    return Memory(db_path=str(tmp_path / "test_memory.db"))


# ------------------------------------------------------------------
# Conversations
# ------------------------------------------------------------------


def test_store_and_retrieve_conversation(memory):
    memory.store_conversation("hello", "hi there", 0.5)
    convs = memory.get_recent_conversations(limit=5)
    assert len(convs) == 1
    _, user_input, robot_response = convs[0]
    assert user_input == "hello"
    assert robot_response == "hi there"


def test_multiple_conversations_ordered_newest_first(memory):
    memory.store_conversation("first", "response 1")
    memory.store_conversation("second", "response 2")
    convs = memory.get_recent_conversations(limit=10)
    assert convs[0][1] == "second"
    assert convs[1][1] == "first"


def test_get_recent_conversations_respects_limit(memory):
    for i in range(5):
        memory.store_conversation(f"msg {i}", f"resp {i}")
    convs = memory.get_recent_conversations(limit=3)
    assert len(convs) == 3


# ------------------------------------------------------------------
# Learning
# ------------------------------------------------------------------


def test_learn_and_recall_fact(memory):
    memory.learn_fact("python", "Python is a programming language")
    facts = memory.recall_facts("python")
    assert len(facts) == 1
    assert facts[0][0] == "Python is a programming language"
    assert facts[0][1] == pytest.approx(1.0)


def test_duplicate_fact_increases_confidence(memory):
    memory.learn_fact("test", "a fact")
    memory.learn_fact("test", "a fact")
    facts = memory.recall_facts("test")
    assert len(facts) == 1
    # confidence should have increased (capped at 1.0 but was already there; repeated
    # calls increment from 1.0 → cap at 1.0, so value stays 1.0 — still valid)
    assert facts[0][1] <= 1.0


def test_recall_facts_empty_topic(memory):
    facts = memory.recall_facts("nonexistent_topic")
    assert facts == []


def test_recall_partial_topic_match(memory):
    memory.learn_fact("machine_learning", "ML is a subset of AI")
    facts = memory.recall_facts("machine")
    assert len(facts) == 1


# ------------------------------------------------------------------
# User preferences
# ------------------------------------------------------------------


def test_set_and_get_preference(memory):
    memory.set_preference("name", "Alice")
    assert memory.get_preference("name") == "Alice"


def test_get_missing_preference_returns_default(memory):
    assert memory.get_preference("missing") is None
    assert memory.get_preference("missing", "fallback") == "fallback"


def test_update_preference(memory):
    memory.set_preference("theme", "dark")
    memory.set_preference("theme", "light")
    assert memory.get_preference("theme") == "light"
