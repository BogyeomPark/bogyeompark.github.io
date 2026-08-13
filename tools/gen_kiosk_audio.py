# -*- coding: utf-8 -*-
"""Render the kiosk demo's spoken order to assets/demos/kiosk/audio/order.mp3.

Shipped as a file rather than spoken by the browser: most machines have no
English voice installed at all, and the ones that do each pick a different
voice at a different rate, which is not a stimulus you can time people
against. The clip is the only thing the demo ever says, and it is played
once, before the task — as in the study, where the instruction was given
verbally beforehand and the kiosk itself said nothing.

    pip install edge-tts
    python tools/gen_kiosk_audio.py

Keep PIN in step with the PIN constant in assets/demos/kiosk.js.
"""
import asyncio
import os

import edge_tts

VOICE = "en-US-AriaNeural"   # female, US English
RATE = "-5%"
PIN = "6289"

OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "demos", "kiosk", "audio", "order.mp3",
)

# All six things the task asks for, in the order the kiosk asks them, because
# the study's spoken instruction covered all six: "The place to eat is a
# restaurant. Please use the kiosk to order a shrimp burger, cheese sticks, and
# a Coca-Cola. Use a credit card as the payment method, and the card payment
# password is 6289." (JMIR 2024;26:e54538). Leaving the place and the payment
# method out made two of the six steps unscoreable.
# Verbatim from the paper, with only the password spaced out so it is read as
# four digits rather than "six thousand two hundred eighty-nine". What to press
# afterwards is written on the page, not spoken, so the clip stays the study's
# own sentence and nothing else.
ORDER = (
    "The place to eat is a restaurant. "
    "Please use the kiosk to order a shrimp burger, cheese sticks, and a Coca-Cola. "
    "Use a credit card as the payment method, "
    "and the card payment password is " + " ".join(PIN) + "."
)


async def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    await edge_tts.Communicate(ORDER, VOICE, rate=RATE).save(OUT)
    print("%d bytes  %s" % (os.path.getsize(OUT), OUT))
    print(ORDER)


asyncio.run(main())
