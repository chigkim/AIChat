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
import random
import json
import argparse
from tts import generate_speech

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
system_prompt = config["system_prompt"]
topic = config["topic"]
a_profile = config["a_profile"]
b_profile = config["b_profile"]
intro = config["intro"]


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


def generate_audio(text, voice, pan=0.5, speed=1.0, lang="en-us"):
    samples, sample_rate = generate_speech(text, voice=voice, speed=speed, lang=lang)
    samples = np.concatenate([samples, random_pause(sample_rate=sample_rate)])
    angle = pan * np.pi / 2
    l = np.cos(angle)
    r = np.sin(angle)
    samples = np.column_stack((samples * l, samples * r))
    return samples, sample_rate


def play(samples, sample_rate):
    sd.play(samples, sample_rate)
    estz = pytz.timezone("US/Eastern")
    date = datetime.now(pytz.utc).astimezone(estz).strftime("%H-%M-%S")
    sf.write(f"samples/{date}.wav", samples, sample_rate)
    sd.wait()


a_client = OpenAI(base_url=a_base_url, api_key=a_api_key)
b_client = OpenAI(base_url=b_base_url, api_key=b_api_key)

a_system_prompt = f"""{system_prompt}
{topic}
{a_profile}"""
print(f"System Prompt for {a_model}: {a_system_prompt}")
b_system_prompt = f"""{system_prompt}
{topic}
{b_profile}"""
print(f"\nSystem Prompt for {b_model}: {b_system_prompt}")
print("\nPress control+c to stop and save the conversation.\n")

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
        a_messages.append({"role": "assistant", "content": response})
        b_messages.append({"role": "user", "content": response})
        samples, sample_rate = generate_audio(response, a_voice, 0.55)
        wavs.append(samples)
        while play_thread.is_alive():
            time.sleep(0.1)
        play_thread = Thread(target=play, args=(samples, sample_rate))
        play_thread.start()
        response = f"{a_model}: {response}\n"
        print(response)
        file.write(response + "\n")
        response = ask(b_client, b_messages, b_model, temperature)
        b_messages.append({"role": "assistant", "content": response})
        a_messages.append({"role": "user", "content": response})
        samples, sample_rate = generate_audio(response, b_voice, 0.45)
        wavs.append(samples)
        while play_thread.is_alive():
            time.sleep(0.1)
        play_thread = Thread(target=play, args=(samples, sample_rate))
        play_thread.start()
        response = f"{b_model}: {response}\n"
        print(response)
        file.write(response + "\n")
except:
    sd.stop()
    print("Saving podcast.wav and transcript.txt")
    wav = np.concat(wavs)
    sf.write(f"podcast.wav", wav, 24000)
    json.dump(a_messages, codecs.open("chat.json", "w", "utf-8"), indent="4")
