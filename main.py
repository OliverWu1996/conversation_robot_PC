"""Entry point for the Conversation Robot."""

import argparse
import logging
import sys

from robot.brain import Brain
from robot.life import Life
from robot.memory import Memory
from robot.voice import VoiceEngine

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run(voice_mode: bool = False, data_dir: str = "data"):
    """Start the main conversation loop."""
    memory = Memory(db_path=f"{data_dir}/memory.db")
    life = Life(data_path=f"{data_dir}/life.json")
    brain = Brain(memory=memory, life=life)

    voice: VoiceEngine | None = None
    if voice_mode:
        voice = VoiceEngine()
        if not voice.available:
            print(
                "⚠  Voice engine unavailable — falling back to text mode.\n"
                "   Install dependencies: pip install SpeechRecognition pyttsx3 pyaudio"
            )
            voice_mode = False

    status = life.get_status()
    print(
        f"\n🤖  Conversation Robot  (age: {status['age_days']} day(s))\n"
        f"    Mood: {status['mood']}  |  Energy: {status['energy']}  |  "
        f"Happiness: {status['happiness']}\n"
        f"    Type your message, or 'quit' to exit.\n"
    )

    while True:
        try:
            user_input: str | None = None

            if voice_mode and voice and voice.available:
                print("🎤  Listening… (press Ctrl+C to type instead)")
                user_input = voice.listen()
                if user_input is None:
                    # Fallback to text if recognition failed
                    user_input = input("You: ").strip()
                else:
                    print(f"You (voice): {user_input}")
            else:
                user_input = input("You: ").strip()

            if not user_input:
                continue

            response = brain.process(user_input)
            print(f"Robot: {response}")

            if voice_mode and voice:
                voice.speak(response)

            if user_input.lower() in ("quit", "exit", "bye", "goodbye"):
                break

        except KeyboardInterrupt:
            print("\nRobot: Goodbye!")
            break
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(
        description="Conversation Robot with VASR and continuous learning."
    )
    parser.add_argument(
        "--voice", action="store_true", help="Enable voice mode (VASR)"
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        metavar="DIR",
        help="Directory for persistent data (default: data/)",
    )
    args = parser.parse_args()
    run(voice_mode=args.voice, data_dir=args.data_dir)


if __name__ == "__main__":
    main()
