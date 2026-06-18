"""VASR — Voice Activated Speech Recognition engine."""

import logging

logger = logging.getLogger(__name__)


class VoiceEngine:
    """Wraps speech recognition (STT) and text-to-speech (TTS) capabilities.

    If the required libraries (*SpeechRecognition*, *pyttsx3*, *PyAudio*) are
    not installed, voice features are gracefully disabled and the application
    falls back to text-only mode.
    """

    def __init__(self, language: str = "en-US"):
        self.language = language
        self._recognizer = None
        self._tts_engine = None
        self._available = False
        self._setup()

    def _setup(self):
        try:
            import speech_recognition as sr  # noqa: PLC0415
            import pyttsx3  # noqa: PLC0415

            self._recognizer = sr.Recognizer()
            self._tts_engine = pyttsx3.init()
            self._available = True
            logger.info("Voice engine initialised successfully.")
        except ImportError:
            logger.warning(
                "speech_recognition or pyttsx3 not available — voice features disabled."
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not initialise voice engine: %s", exc)

    @property
    def available(self) -> bool:
        """``True`` when both STT and TTS are functional."""
        return self._available

    # ------------------------------------------------------------------
    # Speech-to-Text
    # ------------------------------------------------------------------

    def listen(self, timeout: int = 5) -> str | None:
        """Capture microphone input and return the recognised text.

        Returns ``None`` if recognition fails or voice is not available.
        """
        if not self._available:
            return None
        try:
            import speech_recognition as sr  # noqa: PLC0415

            with sr.Microphone() as source:
                logger.info("Listening…")
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self._recognizer.listen(source, timeout=timeout)
            text = self._recognizer.recognize_google(audio, language=self.language)
            logger.info("Recognised: %s", text)
            return text
        except Exception as exc:  # noqa: BLE001
            logger.debug("Voice recognition error: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Text-to-Speech
    # ------------------------------------------------------------------

    def speak(self, text: str):
        """Synthesise *text* as audio output."""
        if not self._available or not text:
            return
        try:
            self._tts_engine.say(text)
            self._tts_engine.runAndWait()
        except Exception as exc:  # noqa: BLE001
            logger.warning("TTS error: %s", exc)
