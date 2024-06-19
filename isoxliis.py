import rp2
import time
from rp2 import PIO
from machine import Pin, PWM
import usb.device
from usb.device.keyboard import KeyboardInterface, KeyCode as KC


"""
ISOXLIIS Keyboard Firmware v0.0.1

Requires pico_usb-v1.23.0-1-pimoroni-micropython.uf2
From: https://github.com/pimoroni/pimoroni-pico/releases/tag/v1.23.0-1

At startup hold:
    - ESC to exit this program
    - Q to disable USB output (for debugging)
"""


keymap = [[
    KC.ESCAPE,    KC.Q, KC.W, KC.E, KC.R, KC.T, KC.Y, KC.U, KC.I, KC.O, KC.P,           KC.ENTER,
    KC.LEFT_SHIFT, KC.A, KC.S, KC.D, KC.F, KC.G, KC.H, KC.J, KC.K, KC.L,   KC.BACKSLASH, 0,
    0,              KC.Z, KC.X, KC.C, KC.V, KC.B, KC.N, KC.M, KC.COMMA, KC.DOT,   KC.UP, KC.HASH,
    KC.LEFT_UI, KC.LEFT_CTRL, KC.LEFT_ALT, 0, 0, KC.SPACE, 0, 0, 0,    KC.LEFT, KC.DOWN, KC.RIGHT
    ], [
    KC.TILDE,     KC.N1, KC.N2, KC.N3, KC.N4, KC.N5, KC.N6, KC.N7, KC.N8, KC.N9, KC.N0, KC.BACKSPACE,
    KC.LEFT_SHIFT, KC.OPEN_BRACKET, KC.CLOSE_BRACKET, KC.D, KC.F, KC.G, KC.H, KC.J, KC.MINUS, KC.EQUAL,   KC.SLASH, 0,
    0,              KC.Z, KC.X, KC.C, KC.V, KC.B, KC.N, KC.M, KC.COMMA, KC.INSERT,   KC.PAGEUP, KC.DELETE,
    KC.LEFT_UI, KC.LEFT_CTRL, KC.LEFT_ALT, 0, 0, KC.PRINTSCREEN, 0, 0, 0,    KC.HOME, KC.PAGEDOWN, KC.END
]]

ROWS = [18, 19, 20, 21]
COLS = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

# Build ourselves a lookup table of keycode labels
CODE_TO_KEY = {v: k for k, v in KC.__dict__.items()}

# Set up our columns, must be input/PULL_UP
COL_PINS = [Pin(col, Pin.IN, Pin.PULL_UP) for col in COLS]

# PWM the LED for fun and debug!
LED_PWM = PWM(Pin("LED", Pin.OUT))
LED_PWM.freq(4200)


# This PIO program is deliberately verbose to make grabbing the column bits easier
# We just "set" each row pin low in turn and load all 12 column pins
# ISOXLIIS is active-low, so zero bits indicate a pressed key
@rp2.asm_pio(
        set_init=(rp2.PIO.OUT_HIGH, rp2.PIO.OUT_HIGH, rp2.PIO.OUT_HIGH, rp2.PIO.OUT_HIGH),
        fifo_join=PIO.JOIN_RX,
        in_shiftdir=PIO.SHIFT_RIGHT,
        autopush=False)
def matrix_scan():
    wrap_target()

    set(pins, 0b1011).delay(3)
    in_(pins, 12)
    set(pins, 0b0111).delay(3)
    in_(pins, 12)
    push()

    set(pins, 0b1110).delay(3)
    in_(pins, 12)
    set(pins, 0b1101).delay(3)
    in_(pins, 12)
    push()

    wrap()


def scan_keys():
    matrix = 0

    # Grab the two FIFO entries that make up one scan cycle
    # and combine them into a single 48-bit bitmap
    for _ in range(2):
        # Shift the scan result left to make room
        matrix <<= 24
        # Shift the FIFO entry right 8-bits
        matrix |= sm.get(None, 8)

    # Invert active-low inputs
    matrix ^= 0xffffffffffff

    return matrix


def main():
    last_matrix = 0
    led_duty = 0

    # Disable USB if Q (second-most key from the top left) is pressed
    usb_enabled = (scan_keys() ^ 0xffffffffffff) & 0b10

    if usb_enabled:
        k = KeyboardInterface()
        usb.device.get().init(k, builtin_driver=True)

    try:
        while True:
            matrix = scan_keys()

            # Slowly make the LED brighter if any key is pressed/held
            # and fade it out if none are pressed/held
            led_duty += 5 if matrix > 0 else -2
            led_duty = min(512, max(0, led_duty))
            LED_PWM.duty_u16(1000 + led_duty * 100)

            if matrix != last_matrix:
                matrix_changed = matrix ^ last_matrix
                last_matrix = matrix

                keys = []

                for n in range(48):
                    mask = 0b1 << n

                    # This is a very crude layer setup
                    # 0x1000000 is the tab key
                    # It's the left-most 0 in the layers of our keymap
                    layer = 1 if matrix & 0x1000000 else 0

                    code = keymap[layer][n]

                    key_changed = matrix_changed & mask
                    key_pressed = matrix & mask

                    if key_pressed:
                        keys.append(code)

                    # Handy debug stuff, hold Q on startup to disable USB
                    # and see this in Thonny!
                    if not usb_enabled and key_changed:
                        col = n % 12
                        row = n // 12
                        key = CODE_TO_KEY.get(code, "N/A")
                        state = "pressed" if key_pressed else "released"
                        print(f"{key} {col, row} {state}!")

                if usb_enabled:
                    k.send_keys(keys)

                time.sleep_ms(1)

    except KeyboardInterrupt:
        pass

    finally:
        sm.active(0)


# Start running the PIO so we can scan in the bailout keys
sm = rp2.StateMachine(0, matrix_scan, freq=10_000, set_base=Pin(ROWS[0]), in_base=Pin(COLS[0]))
sm.active(1)

if scan_keys() & 0b1:
    print("ESC held, exiting!")
    sm.active(0)
else:
    main()
