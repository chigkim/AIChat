from kokoro_onnx import Kokoro
import os
from utils import download


def generate_speech(text, voice, speed=1.0, lang="en-us"):
    return kokoro.create(text, voice=voice, speed=speed, lang=lang)


if not os.path.exists("kokoro-v1.0.onnx"):
    print("Downloading kokoro-v1.0.onnx")
    download(
        "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
        "kokoro-v1.0.onnx",
    )
    print()
if not os.path.exists("voices-v1.0.bin"):
    print("Downloading voices-v1.0.bin")
    download(
        "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
        "voices-v1.0.bin",
    )
    print()

kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
