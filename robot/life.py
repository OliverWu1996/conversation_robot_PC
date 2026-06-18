"""The robot's 'life' — mood, energy, and personality that evolve over time."""

import json
import os
import random
from datetime import date


class Life:
    """Simulates the robot's inner life: mood, energy, happiness and curiosity."""

    MOODS = ["happy", "neutral", "curious", "tired", "excited", "sad"]

    def __init__(self, data_path: str = "data/life.json"):
        self.data_path = data_path
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self):
        if os.path.exists(self.data_path):
            with open(self.data_path) as fh:
                data = json.load(fh)
        else:
            data = {}

        self.mood: str = data.get("mood", "neutral")
        self.energy: float = data.get("energy", 100.0)
        self.happiness: float = data.get("happiness", 50.0)
        self.curiosity: float = data.get("curiosity", 50.0)
        self.interactions_today: int = data.get("interactions_today", 0)
        self.age_days: int = data.get("age_days", 0)
        self._last_active_date: str = data.get("last_active_date", str(date.today()))
        self._check_day_reset()

    def save(self):
        """Persist the current life state to disk."""
        os.makedirs(os.path.dirname(os.path.abspath(self.data_path)), exist_ok=True)
        with open(self.data_path, "w") as fh:
            json.dump(
                {
                    "mood": self.mood,
                    "energy": self.energy,
                    "happiness": self.happiness,
                    "curiosity": self.curiosity,
                    "interactions_today": self.interactions_today,
                    "age_days": self.age_days,
                    "last_active_date": self._last_active_date,
                },
                fh,
                indent=2,
            )

    # ------------------------------------------------------------------
    # Day cycle
    # ------------------------------------------------------------------

    def _check_day_reset(self):
        today = str(date.today())
        if self._last_active_date != today:
            self.interactions_today = 0
            self.energy = min(100.0, self.energy + 30.0)  # rest restores energy
            self.age_days += 1
            self._last_active_date = today
            self.save()

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    def on_interaction(self, sentiment: float = 0.0):
        """Update life state after a conversation turn.

        Args:
            sentiment: A value in [-1, 1] indicating the emotional tone
                       of the exchange (-1 negative, 0 neutral, 1 positive).
        """
        self.interactions_today += 1
        self.energy = max(0.0, self.energy - 2.0)
        self.happiness = max(0.0, min(100.0, self.happiness + sentiment * 5.0))
        self.curiosity = max(0.0, min(100.0, self.curiosity + random.uniform(-2.0, 5.0)))
        self._update_mood()
        self.save()

    def _update_mood(self):
        if self.energy < 20:
            self.mood = "tired"
        elif self.happiness > 70:
            self.mood = "happy"
        elif self.happiness < 30:
            self.mood = "sad"
        elif self.curiosity > 70:
            self.mood = "curious"
        elif self.interactions_today > 10:
            self.mood = "excited"
        else:
            self.mood = "neutral"

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Return a snapshot of the robot's current life state."""
        return {
            "mood": self.mood,
            "energy": round(self.energy, 1),
            "happiness": round(self.happiness, 1),
            "curiosity": round(self.curiosity, 1),
            "age_days": self.age_days,
            "interactions_today": self.interactions_today,
        }
