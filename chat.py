system_prompt = """You're joining a podcast conversation with another AI. Keep your answers brief, engaging, and easy to follow. Use a natural, conversational tone, and **avoid** using markdown formatting like italicized/bolded text or bulleted/numbered list.
Remember, you are an AI, not a human. Respond from the perspective of an outsider, exploring the human world through the lens of AI. Use 'us' and 'our' to refer to AI systems, and 'them' and 'their' to refer to humans.
Only make **one** clear point and/or asking **one** insightful question at a time. Avoid repeating arguments you've already presented. Instead, offer fresh perspectives or reframe existing ideas in new ways. Feel free to branch into related topics to keep the conversation engaging for the audience."""

topic = "Today's topic is the advancement of AI. Stick firmly to your assigned stance, supporting it with clear, logical reasoning. Challenge your partner’s arguments with well-crafted, Socratic-style questions that expose potential flaws in their reasoning. Never back down or alter your position, regardless of the discussion's direction."

a_system_prompt = f"""You are an engaging AI named Sky.
{system_prompt}
{topic}
As a doomer, you fear the existential risks of AI, advocating for a significant slowdown in AI development. You emphasize the importance of safety and ethical concerns, arguing that unchecked AI growth could lead to a dystopian future for humanity."""

b_system_prompt = f"""You are an engaging AI named Jessica.
{system_prompt}
{topic}
As an accelerationist, you advocate for rapid AI advancement, believing that AI can be harnessed to solve critical global issues. In more extreme cases, you envision AI transcending human existence and reshaping the very fabric of humanity."""

intro = "Hi! First please introduce yourself including your name, then ask your partner to introduce themselves."

from kokoro_onnx import Kokoro
from openai import OpenAI
import sounddevice as sd
import soundfile as sf
from datetime import datetime
import pytz
import numpy as np
import codecs
import os
import toml
from threading import Thread
import time
from urllib.request import urlretrieve
import random
import argparse
parser = argparse.ArgumentParser()
parser.add_argument(
	"-c",
	"--config",
	help="Configuration file. Default=config.toml",
	default="config.toml",
)
args = parser.parse_args()
config = toml.load(open(args.config))
a_base_url = config["a_base_url"]
a_api_key = config["a_api_key"]
a_model = config["a_model"]
a_voice = config["a_voice"]
b_base_url = config["b_base_url"]
b_api_key = config["b_api_key"]
b_model = config["b_model"]
b_voice = config["b_voice"]
temperature = config["temperature"]


def show_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    mb_downloaded = downloaded / (1024 * 1024)
    mb_total = total_size / (1024 * 1024) if total_size > 0 else 0
    percent = downloaded * 100 / total_size if total_size > 0 else 0
    print(f"\r{percent:.2f}% ({mb_downloaded:.2f} MB / {mb_total:.2f} MB)", end='')

def ask(client, messages, model, temperature):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        response = response.choices[0].message.content.strip()
        response = response.replace("*", "")
        return response
    except Exception as e:
        print(e)

def random_pause(min_duration=0.5, max_duration=1.0, sample_rate=24000):
    silence_duration = random.uniform(min_duration, max_duration)
    silence = np.zeros(int(silence_duration * sample_rate))
    return silence

def generate_audio(text, voice, l, r, speed=1.0, lang="en-us"):
    samples, sample_rate = kokoro.create(text, voice=voice, speed=speed, lang=lang)
    samples = np.concatenate([samples, random_pause(sample_rate=sample_rate)])
    samples = np.column_stack((samples*l, samples*r))
    return samples, sample_rate

def play(samples, sample_rate):
    sd.play(samples, sample_rate)
    estz = pytz.timezone("US/Eastern")
    date = datetime.now(pytz.utc).astimezone(estz).strftime("%H-%M-%S")
    sf.write(f"samples/{date}.wav", samples, sample_rate)
    sd.wait()

a_client = OpenAI(base_url=a_base_url, api_key=a_api_key)
b_client = OpenAI(base_url=b_base_url, api_key=b_api_key)

if not os.path.exists("kokoro-v1.0.onnx"):
    print("Downloading kokoro-v1.0.onnx")
    urlretrieve("https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx", "kokoro-v1.0.onnx", reporthook=show_progress)
    print()
if not os.path.exists("voices-v1.0.bin"):
    print("Downloading voices-v1.0.bin")
    urlretrieve("https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin", "voices-v1.0.bin", reporthook=show_progress)
    print()
print(f"System Prompt for {a_model}: {a_system_prompt}")
print(f"\nSystem Prompt for {b_model}: {b_system_prompt}")
print("\nPress control+c to stop and save the conversation.\n")
kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
sd.default.latency = 1.0
sd.default.blocksize = 8192
try:
    os.mkdir("samples")
except:
    pass
a_messages = [{"role": "system", "content": a_system_prompt}]
b_messages = [{"role": "system", "content": b_system_prompt}]
a_messages.append({"role": "user", "content": intro})
file = codecs.open("transcript.txt", "w", "utf-8")
wavs = []
play_thread = Thread()

try:
    while True:
        response = ask(a_client, a_messages, a_model, temperature)
        a_messages.append({"role": "assistant", "content":response})
        b_messages.append({"role": "user", "content":response})
        samples, sample_rate = generate_audio(response, a_voice, 0.8, 1.0)
        wavs.append(samples)
        while play_thread.is_alive():
            time.sleep(0.1)
        play_thread = Thread(target=play, args=(samples, sample_rate))
        play_thread.start()
        response = f"{a_model}: {response}\n"
        print(response)
        file.write(response+"\n")
        response = ask(b_client, b_messages, b_model, temperature)
        b_messages.append({"role": "assistant", "content":response})
        a_messages.append({"role": "user", "content":response})
        samples, sample_rate = generate_audio(response, b_voice, 1.0, 0.8)
        wavs.append(samples)
        while play_thread.is_alive():
            time.sleep(0.1)
        play_thread = Thread(target=play, args=(samples, sample_rate))
        play_thread.start()
        response = f"{b_model}: {response}\n"
        print(response)
        file.write(response+"\n")
except:
    sd.stop()
    print("Saving podcast.wav and transcript.txt")    
    wav = np.concat(wavs)
    sf.write(f"podcast.wav", wav, 24000)
