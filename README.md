# ISOXLIIS MicroPython Software

This is a very simple demo using MicroPython's USB HID features to drive
the ISOXLIIS keyboard.

Requires pico_usb-v1.23.0-1-pimoroni-micropython.uf2 
From: https://github.com/pimoroni/pimoroni-pico/releases/tag/v1.23.0-1

Features:

* Uses PIO to scan the matrix
* Uses MicroPython USB (easy to customise)
* Bailout keys, hold one of the following before plugging in USB or running isoxliis.py:
   * ESC - Do not boot firmware
   * Q - Do not enable USB
* Two layers
* Generator-based macros

## Macros

ISOXLIIS macros are written as Python generators. When you press a key a macro
generator is added to the macro queue. When the generator finishes, it's removed
and the next macros in the queue starts.

If a macro returns a keycode, eg: `KC.SPACE` then that "key" will be pressed.

If a macro returns 0 then it will trigger a HID transmission, useful for clearing
keys. You must add 0 between successive presses of the same key, or it will just
appear to be held down.

If a macro returns -1 then it will do nothing, useful for adding delays.

If a macro returns a generator, ie: you `yield x()` instead of `yield from x()`
then it will be added to the top of the macro queue.

If a macro returns a function, ie: you `yield x` instead of `yield x()` it will
be called and added to the top of the macro queue.

This effectively means you can shorthand chain macros, like so:

```python
from isoxliis_macro import hello_world, macos_ss_window

def my_mixed_macro():
   yield hello_world
   yield macos_ss_window
```

This will type "Hello World" and then hit the macOS screenshot key combo:
`Command + Shift + 4` followed by a brief pause and `Space` to switch to
window capture.

To type a particular key code, just `yield` it, like so:

```python
from nkro_keyboard import KeyCode as KC

def type_o():
   yield KC.O
```

To use a macro, just replace a keycode in the `keymap` with the macro
function name. I've done this with `macos_ss_window` on Fn + Spacebar.

### Mixing Macros

If you want to combine multiple macros, or re-use macros within other
macros you can just `yield` them from your macro as above.

This can get messy with longer combos, but you can use `yield from` to
avoid the repetition, like so:

```python
def macos_ss_window():
    yield from (
        macos_ss_select(),
        wait(50),
        KC.SPACE
    )
```

### Special Characters

Characters which don't have a single keycode mapping, such as ^ (shift + 6)
and many others are mapped in the `charmap`. Right now this only supports
single scancodes, with or without shift.

It's also been tested only on macOS so far, and the text in `macro_test` is
what you should expect to see on screen if your OS/Language match mine.

Otherwise, ymmv, remap it!
