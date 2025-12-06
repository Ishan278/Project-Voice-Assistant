import sys
import datetime
import webbrowser
import urllib.parse

try:
	import speech_recognition as sr
except Exception:
	sr = None

try:
	import pyttsx3
except Exception:
	pyttsx3 = None


def _init_tts():
	if pyttsx3 is None:
		return None
	try:
		engine = pyttsx3.init()
		engine.setProperty('rate', 160)
		return engine
	except Exception:
		return None


TTS_ENGINE = _init_tts()


def speak(text: str) -> None:
	"""Speak the given text using TTS when available, otherwise print it.

	This function is intentionally simple so the project can run without
	audio dependencies installed. Use the `pyttsx3` package for offline
	TTS if available.
	"""
	if TTS_ENGINE is not None:
		try:
			TTS_ENGINE.say(text)
			TTS_ENGINE.runAndWait()
			return
		except Exception:
			pass
	print(text)


def listen_voice(timeout: float = 5.0) -> str | None:
	"""Attempt to listen from the microphone and return recognized text.

	Returns None on failure or when speech libraries are not available.
	"""
	if sr is None:
		return None

	try:
		import sounddevice
		import soundfile
	except ImportError:
		print("*Error:* sounddevice or soundfile not installed")
		return None

	recognizer = sr.Recognizer()
	try:
		print("Listening...")
		# Record audio for up to `timeout` seconds
		sample_rate = 16000
		duration = timeout
		audio_data = sounddevice.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype='float32')
		sounddevice.wait()
		print("Audio captured, processing...")
		
		# Convert to audio_data to speech_recognition format
		audio_data_int16 = (audio_data * 32767).astype('int16')
		audio = sr.AudioData(audio_data_int16.tobytes(), sample_rate, 2)
		
	except Exception as e:
		print(f"*Error:* Recording failed: {e}")
		return None

	try:
		text = recognizer.recognize_google(audio)
		print(f"Recognized: {text}")
		return text
	except sr.UnknownValueError:
		print("*Error:* Could not understand audio. Please try again.")
		return None
	except sr.RequestError as e:
		print(f"*Error:* Network/API error: {e}")
		return None
	except Exception as e:
		print(f"*Error:* Recognition failed: {e}")
		return None


def open_web_search(query: str) -> None:
	"""Open the default browser with a Google search for `query`."""
	url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
	webbrowser.open(url)


def handle_command(command: str) -> bool:
	"""Handle a single user command.

	Returns True to continue the loop, False to exit.
	"""
	if not command:
		speak("I didn't catch that. Try typing your command.")
		return True

	text = command.strip().lower()

	if any(greet in text for greet in ("hello", "hi", "hey")):
		speak("Hello! How can I help you today?")
		return True

	if "time" in text:
		now = datetime.datetime.now()
		speak(now.strftime("The time is %H:%M."))
		return True

	if "date" in text:
		today = datetime.date.today()
		speak(today.strftime("Today's date is %B %d, %Y."))
		return True

	if text.startswith("search ") or text.startswith("search for "):
		# accept: "search for python web scraping" or "search python"
		query = text.split(" ", 1)[1]
		speak(f"Searching the web for: {query}")
		open_web_search(query)
		return True

	if text.startswith("open "):
		target = text.split(" ", 1)[1]
		speak(f"Opening {target}")
		open_web_search(target)
		return True

	if text in ("exit", "quit", "stop", "bye"):
		speak("Goodbye!")
		return False

	# Fallback: if user says a short query, treat as web search
	if len(text) > 0:
		speak("I don't have a dedicated handler for that. Searching the web.")
		open_web_search(text)
		return True

	return True


def main():
	speak("Voice assistant starting. Say 'hello', ask for the time or date, or say 'search' followed by your query.")
	speak("If microphone isn't available, type your command. Type 'exit' to quit.")

	use_voice = sr is not None
	if use_voice:
		speak("Voice input appears available. Listening for commands...")
	else:
		speak("Speech libraries not installed — falling back to text input.")

	while True:
		command = None
		if use_voice:
			command = listen_voice()

		if command is None:
			try:
				command = input('> ')
			except (KeyboardInterrupt, EOFError):
				speak("Goodbye!")
				break

		cont = handle_command(command)
		if not cont:
			break


if __name__ == '__main__':
	main()

