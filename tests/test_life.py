"""Tests for robot.life — the robot's evolving life state."""

import json
import pytest
from robot.life import Life


@pytest.fixture
def life(tmp_path):
    return Life(data_path=str(tmp_path / "life.json"))


# ------------------------------------------------------------------
# Initial state
# ------------------------------------------------------------------


def test_initial_mood_is_valid(life):
    assert life.mood in Life.MOODS


def test_initial_energy_is_in_range(life):
    assert 0 <= life.energy <= 100


def test_initial_happiness_is_in_range(life):
    assert 0 <= life.happiness <= 100


def test_initial_curiosity_is_in_range(life):
    assert 0 <= life.curiosity <= 100


# ------------------------------------------------------------------
# Interactions
# ------------------------------------------------------------------


def test_interaction_decreases_energy(life):
    life.energy = 50.0
    life.on_interaction(sentiment=0.0)
    assert life.energy < 50.0


def test_positive_sentiment_increases_happiness(life):
    life.happiness = 50.0
    life.on_interaction(sentiment=1.0)
    assert life.happiness > 50.0


def test_negative_sentiment_decreases_happiness(life):
    life.happiness = 50.0
    life.on_interaction(sentiment=-1.0)
    assert life.happiness < 50.0


def test_energy_does_not_go_below_zero(life):
    life.energy = 1.0
    for _ in range(10):
        life.on_interaction(sentiment=0.0)
    assert life.energy >= 0.0


def test_happiness_stays_within_bounds(life):
    life.happiness = 99.0
    for _ in range(5):
        life.on_interaction(sentiment=1.0)
    assert life.happiness <= 100.0

    life.happiness = 1.0
    for _ in range(5):
        life.on_interaction(sentiment=-1.0)
    assert life.happiness >= 0.0


# ------------------------------------------------------------------
# Mood transitions
# ------------------------------------------------------------------


def test_low_energy_triggers_tired_mood(life):
    life.energy = 10.0
    life._update_mood()
    assert life.mood == "tired"


def test_high_happiness_triggers_happy_mood(life):
    life.energy = 80.0
    life.happiness = 80.0
    life._update_mood()
    assert life.mood == "happy"


def test_low_happiness_triggers_sad_mood(life):
    life.energy = 80.0
    life.happiness = 20.0
    life._update_mood()
    assert life.mood == "sad"


# ------------------------------------------------------------------
# Persistence
# ------------------------------------------------------------------


def test_save_and_reload(life, tmp_path):
    life.mood = "happy"
    life.energy = 77.0
    life.save()

    loaded = Life(data_path=str(tmp_path / "life.json"))
    assert loaded.mood == "happy"
    assert loaded.energy == pytest.approx(77.0)


# ------------------------------------------------------------------
# Status
# ------------------------------------------------------------------


def test_get_status_contains_expected_keys(life):
    status = life.get_status()
    for key in ("mood", "energy", "happiness", "curiosity", "age_days", "interactions_today"):
        assert key in status
