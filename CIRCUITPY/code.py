""" HEADER """
# pylint: disable=bare-except

import time
import math
import gc
from digitalio import DigitalInOut, Direction, Pull
import audiocore
import audioio
import busio
import board
import neopixel
import adafruit_lis3dh

# COLORS
RED_COLOR = (255, 0, 0)
RED_NAME = "IMPERIAL.wav" #"FATES.wav"
RED_TIME = 9.5 #17

BLUE_COLOR = (0, 50, 255)
BLUE_NAME = "BLUE.wav"
BLUE_TIME = 15

GREEN_COLOR = (0,255,0)
GREEN_NAME = "LUKE.wav"
GREEN_TIME = 15

YELLOW_COLOR = (255, 239, 0)
YELLOW_NAME = "REY.wav"
YELLOW_TIME = 12

WHITE_COLOR = (0, 0, 0)
WHITE_NAME = "AHSOKA.wav"
WHITE_TIME = 13

COLOR = BLUE_COLOR
character = 1

# TIMES
LIGHTON_TIME = 1.7
LIGHTOFF_TIME = 1.15

# CUSTOMIZE SENSITIVITY HERE: smaller numbers = more sensitive to motion
HIT_THRESHOLD = 350 # 250
SWING_THRESHOLD = 125

NUM_PIXELS = 321
NEOPIXEL_PIN = board.D5
POWER_PIN = board.D10
SWITCH_PIN = board.D9
character_PIN = board.D4

enable = DigitalInOut(POWER_PIN)
enable.direction = Direction.OUTPUT
enable.value =False

red_led = DigitalInOut(board.D11)
red_led.direction = Direction.OUTPUT
green_led = DigitalInOut(board.D12)
green_led.direction = Direction.OUTPUT
blue_led = DigitalInOut(board.D13)
blue_led.direction = Direction.OUTPUT

audio = audioio.AudioOut(board.A0)     # Speaker
mode = 0                               # Initial mode = OFF

strip = neopixel.NeoPixel(NEOPIXEL_PIN, NUM_PIXELS, brightness=1, auto_write=False)
strip.fill(0)                          # NeoPixels off ASAP on startup
strip.show()

switch = DigitalInOut(SWITCH_PIN)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

change = DigitalInOut(character_PIN)
change.direction = Direction.INPUT
change.pull = Pull.UP                        # Initial mode = LIGHT

time.sleep(0.1)

# Set up accelerometer on I2C bus, 4G range:
i2c = busio.I2C(board.SCL, board.SDA)
accel = adafruit_lis3dh.LIS3DH_I2C(i2c)
accel.range = adafruit_lis3dh.RANGE_4_G

# "Idle" color is 1/4 brightness, "swinging" color is full brightness...
COLOR_IDLE = (int(COLOR[0] / 1), int(COLOR[1] / 1), int(COLOR[2] / 1))
COLOR_SWING = COLOR
COLOR_HIT = (255, 255, 255)  # "hit" color is white

def play_wav(name, loop=False):
    """
    Play a WAV file in the 'sounds' directory.
    @param name: partial file name string, complete name will be built around
                 this, e.g. passing 'foo' will play file 'sounds/foo.wav'.
    @param loop: if True, sound will repeat indefinitely (until interrupted
                 by another sound).
    """
    print("playing", name)
    try:
        wave_file = open('sounds/' + name, 'rb')
        wave = audiocore.WaveFile(wave_file)
        audio.play(wave, loop=loop)
    except:
        print("NOPE")
        return

def power(sound, duration, reverse):
    """
    Animate NeoPixels with accompanying sound effect for power on/off and color change.
    @param sound:    sound name (similar format to play_wav() above)
    @param duration: estimated duration of sound, in seconds (>0.0)
    @param reverse:  if True, do power-off effect (reverses animation)
    """
    if reverse:
        prev = NUM_PIXELS
    else:
        prev = 0
    gc.collect()                   # Tidy up RAM now so animation's smoother
    start_time = time.monotonic()  # Save audio start time
    play_wav(sound)
    while True:
        elapsed = time.monotonic() - start_time  # Time spent playing sound
        if elapsed > duration:                   # Past sound duration?
            break                                # Stop animating
        fraction = elapsed / duration            # Animation time, 0.0 to 1.0
        if reverse:
            fraction = 1.0 - fraction            # 1.0 to 0.0 if reverse
        fraction = math.pow(fraction, 0.5)       # Apply nonlinear curve
        threshold = int(NUM_PIXELS * fraction + 0.5)
        num = threshold - prev # Number of pixels to light on this pass
        if num != 0:
            if reverse:
                strip[threshold:prev] = [0] * -num
            else:
                strip[prev:threshold] = [COLOR_IDLE] * num
            strip.show()
            # NeoPixel writes throw off time.monotonic() ever so slightly
            # because interrupts are disabled during the transfer.
            # We can compensate somewhat by adjusting the start time
            # back by 30 microseconds per pixel.
            start_time -= NUM_PIXELS * 0.00003
            prev = threshold

    if reverse:
        strip.fill(0)                            # At end, ensure strip is off
    else:
        strip.fill(COLOR_IDLE)                   # or all pixels set on
    strip.show()
    while audio.playing:                         # Wait until audio done
        pass

def mix(color_1, color_2, weight_2):
    """
    Blend between two colors with a given ratio.
    @param color_1:  first color, as an (r,g,b) tuple
    @param color_2:  second color, as an (r,g,b) tuple
    @param weight_2: Blend weight (ratio) of second color, 0.0 to 1.0
    @return: (r,g,b) tuple, blended color
    """
    if weight_2 < 0.0:
        weight_2 = 0.0
    elif weight_2 > 1.0:
        weight_2 = 1.0
    weight_1 = 1.0 - weight_2
    return (int(color_1[0] * weight_1 + color_2[0] * weight_2),
            int(color_1[1] * weight_1 + color_2[1] * weight_2),
            int(color_1[2] * weight_1 + color_2[2] * weight_2))

# Main program loop, repeats indefinitely
while True:

    red_led.value = True

    # Since the Featehrwing has so little memory you can'y have all the characters
    if not change.value:                   # button pressed?
        if character == 0:
            COLOR = BLUE_COLOR              # set it to new color and re-light
            # "Idle" color is 1/4 brightness, "swinging" color is full brightness...
            COLOR_IDLE = (int(COLOR[0] / 1), int(COLOR[1] / 1), int(COLOR[2] / 1))
            COLOR_SWING = COLOR
            COLOR_HIT = (255, 255, 255)  # "hit" color is white
            enable.value = True
            power(BLUE_NAME, BLUE_TIME, False)         # Power up!
            play_wav('idle.wav', loop=True)     # Play background hum sound
            character = 1
        elif character == 1:
            COLOR = RED_COLOR              # set it to new color and re-light
            # "Idle" color is 1/4 brightness, "swinging" color is full brightness...
            COLOR_IDLE = (int(COLOR[0] / 1), int(COLOR[1] / 1), int(COLOR[2] / 1))
            COLOR_SWING = COLOR
            COLOR_HIT = (255, 255, 255)  # "hit" color is white
            enable.value = True
            power(RED_NAME, RED_TIME, False)         # Power up!
            play_wav('idle.wav', loop=True)     # Play background hum sound
            character = 2
        elif character == 2:
            COLOR = YELLOW_COLOR              # set it to new color and re-light
            # "Idle" color is 1/4 brightness, "swinging" color is full brightness...
            COLOR_IDLE = (int(COLOR[0] / 1), int(COLOR[1] / 1), int(COLOR[2] / 1))
            COLOR_SWING = COLOR
            COLOR_HIT = (255, 255, 255)  # "hit" color is white
            enable.value = True
            power(YELLOW_NAME, YELLOW_TIME, False)         # Power up!
            play_wav('idle.wav', loop=True)     # Play background hum sound
            character = 3
        elif character == 3:
            COLOR = GREEN_COLOR              # set it to new color and re-light
            # "Idle" color is 1/4 brightness, "swinging" color is full brightness...
            COLOR_IDLE = (int(COLOR[0] / 1), int(COLOR[1] / 1), int(COLOR[2] / 1))
            COLOR_SWING = COLOR
            COLOR_HIT = (255, 255, 255)  # "hit" color is white
            enable.value = True
            power(GREEN_NAME, GREEN_TIME, False)         # Power up!
            play_wav('idle.wav', loop=True)     # Play background hum sound
            character = 0 #4
        # elif character == 4:
        #     setColors(WHITE_COLOR)
        #     enable.value = True
        #     power(WHITE_NAME, WHITE_TIME, False)         # Power up!
        #     play_wav('idle.wav', loop=True)     # Play background hum sound
        #     character = 0

    if not switch.value:                    # button pressed?
        if mode == 0:                       # If currently off...
            enable.value = True
            power('on.wav', LIGHTON_TIME, False)         # Power up!
            play_wav('idle.wav', loop=True)     # Play background hum sound
            mode = 1                        # ON (idle) mode now
        else:                               # else is currently on...
            power('off.wav', LIGHTOFF_TIME, True)        # Power down
            mode = 0                        # OFF mode now
            enable.value = False
        while not switch.value:             # Wait for button release
            time.sleep(0.2)                 # to avoid repeated triggering

    if mode >= 1:                         # If not OFF mode...
        x, y, z = accel.acceleration # Read accelerometer
        accel_total = x * x + z * z
        # (Y axis isn't needed for this, assuming Hallowing is mounted
        # characterways to stick.  Also, square root isn't needed, since we're
        # just comparing thresholds...use squared values instead, save math.)
        if accel_total > HIT_THRESHOLD:   # Large acceleration = HIT
            TRIGGER_TIME = time.monotonic() # Save initial time of hit
            play_wav('hit.wav')                 # Start playing 'hit' sound
            COLOR_ACTIVE = COLOR_HIT        # Set color to fade from
            mode = 3                        # HIT mode
        elif mode == 1 and accel_total > SWING_THRESHOLD: # Mild = SWING
            TRIGGER_TIME = time.monotonic() # Save initial time of swing
            play_wav('swing.wav')               # Start playing 'swing' sound
            COLOR_ACTIVE = COLOR_SWING      # Set color to fade from
            mode = 2                        # SWING mode
        elif mode > 1:                      # If in SWING or HIT mode...
            if audio.playing:               # And sound currently playing...
                blend = time.monotonic() - TRIGGER_TIME # Time since triggered
                if mode == 2:               # If SWING,
                    blend = abs(0.5 - blend) * 2.0 # ramp up, down
                strip.fill(mix(COLOR_ACTIVE, COLOR_IDLE, blend))
                strip.show()
            else:                           # No sound now, but still MODE > 1
                play_wav('idle.wav', loop=True) # Resume background hum
                strip.fill(COLOR_IDLE)      # Set to idle color
                strip.show()
                mode = 1                    # IDLE mode now
