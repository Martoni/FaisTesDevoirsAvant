#!/usr/bin/env python3
# from https://github.com/alphacep/vosk-api
# prerequisites: as described in https://alphacephei.com/vosk/install and also python module `sounddevice` (simply run command `pip install sounddevice`)
# Example usage using Dutch (nl) recognition model: `python test_microphone.py -m nl`
# For more help run: `python test_microphone.py -h`

import argparse
import queue
import sys
import json
import random
import sounddevice as sd
from text_to_num import text2num

from vosk import Model, KaldiRecognizer


MAX_OPERATION_NB = 5

q = queue.Queue()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


def my_text_2_num(text):
    text = text.strip()
    if text == "de":
        return 2
    try:
        return text2num(text, "fr")
    except ValueError:
        return -1


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-l", "--list-devices", action="store_true",
        help="show list of audio devices and exit")
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser])
    parser.add_argument(
        "-f", "--filename", type=str, metavar="FILENAME",
        help="audio file to store recording to")
    parser.add_argument(
        "-d", "--device", type=int_or_str,
        help="input device (numeric ID or substring)")
    parser.add_argument(
        "-r", "--samplerate", type=int, help="sampling rate")
    parser.add_argument(
        "-m", "--model", type=str,
        help="language model; e.g. en-us, fr, nl; default is en-us")
    args = parser.parse_args(remaining)
    
    try:
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, "input")
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info["default_samplerate"])
            
        model = Model(lang="fr")
    
        with sd.RawInputStream(samplerate=args.samplerate,
                               blocksize = 8000,
                               device=args.device,
                               dtype="int16",
                               channels=1,
                               callback=callback):
    
            rec = KaldiRecognizer(model, args.samplerate)
            count = MAX_OPERATION_NB 
            while count != 0:
                print(f"Courage, plus que {count} opérations")
                a = random.randint(2, 9)
                b = random.randint(2, 9)
                print(f"Combien font {a} x {b} ?")
                while True:
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        res = rec.Result()
                        textvalue = json.loads(res).get("text", None)
                        if textvalue is not None:
                            response = my_text_2_num(textvalue)
                            if textvalue.strip() == "" or response < 0:
                                print("alors ?")
                            else:
                                print(f"(Ta réponse «{textvalue}» -> {response})")
                                if response == a * b:
                                    print("Bien")
                                    count -= 1
                                    break
                                else:
                                    print("Raté")
                                    count = MAX_OPERATION_NB
                                    break

    except KeyboardInterrupt:
        print("\nDone")
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ": " + str(e))
    print("\o/       \o/")
    print("\o/ Bravo \o/")
    print("\o/       \o/")

