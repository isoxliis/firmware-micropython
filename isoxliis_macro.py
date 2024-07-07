import time
from nkro_keyboard import KeyCode as KC


charmap = {
    9: KC.TAB,  # \t
    10: KC.ENTER,
    32: KC.SPACE,
    33: (KC.LEFT_SHIFT, KC.N1),  # !
    34: (KC.LEFT_SHIFT, KC.QUOTE),  # "
    35: (KC.HASH),  # #
    36: (KC.LEFT_SHIFT, KC.N4),  # $
    37: (KC.LEFT_SHIFT, KC.N5),  # %
    38: (KC.LEFT_SHIFT, KC.N7),  # &
    39: (KC.QUOTE),  # '
    40: (KC.LEFT_SHIFT, KC.N9),  # (
    41: (KC.LEFT_SHIFT, KC.N0),  # )
    42: (KC.LEFT_SHIFT, KC.N8),  # *
    43: (KC.LEFT_SHIFT, KC.EQUAL),  # +
    44: KC.COMMA,  # ,
    45: KC.MINUS,  # -
    46: KC.DOT,  # .
    47: KC.SLASH,  # /
    58: (KC.LEFT_SHIFT, KC.SEMICOLON),
    59: KC.SEMICOLON,
    60: (KC.LEFT_SHIFT, KC.COMMA),  # <
    61: KC.EQUAL,
    62: (KC.LEFT_SHIFT, KC.DOT),  # >
    63: (KC.LEFT_SHIFT, KC.SLASH),  # ?
    64: (KC.LEFT_SHIFT, KC.N2),  # @,
    91: KC.OPEN_BRACKET,  # [
    92: KC.BACKSLASH,  # \
    93: KC.CLOSE_BRACKET,  # ]
    94: (KC.LEFT_SHIFT, KC.N6),  # ^
    95: (KC.LEFT_SHIFT, KC.MINUS),  # _
    123: (KC.LEFT_SHIFT, KC.OPEN_BRACKET),  # {
    124: (KC.LEFT_SHIFT, KC.BACKSLASH),  # |
    125: (KC.LEFT_SHIFT, KC.CLOSE_BRACKET),  # }
    126: (KC.LEFT_SHIFT, KC.GRAVE),  # ~
    163: (KC.LEFT_SHIFT, KC.N3)  # £
}

a_to_z = range(ord("a"), ord("z") + 1)
one_to_nine = range(ord("1"), ord("9") + 1)

DO_NOTHING = -1


def wait(delay):
    if delay == 0:
        return
    t_until = time.ticks_ms() + delay
    if time.ticks_diff(t_until, time.ticks_ms()) > 0:
        yield 0
    while time.ticks_diff(t_until, time.ticks_ms()) > 0:
        yield DO_NOTHING


def hold(key, delay, auto_release=True):
    t_until = time.ticks_ms() + delay
    while time.ticks_diff(t_until, time.ticks_ms()) > 0:
        yield key
    if auto_release:
        yield 0


def repeat(key, times, delay=0):
    for _ in range(times):
        yield key
        yield 0
        yield wait(delay)


def scancode(char):
    upper = char.isupper()
    char = ord(char.lower())
    if char in a_to_z:
        if upper:
            return KC.LEFT_SHIFT, char - 97 + KC.A
        else:
            return char - 97 + KC.A
    elif char in one_to_nine:
        return char - 49 + KC.N1
    elif char == 48:
        return KC.N0
    elif k := charmap.get(char):
        return k
    else:
        return 0


def text(text, delay=100):
    last_key = None
    for char in text:
        sc = scancode(char)
        if isinstance(sc, tuple):
            mod, key = sc
            if key == last_key:
                yield 0
            last_key = key
            yield mod
            yield mod, key
        else:
            if sc == last_key:
                yield 0
            last_key = sc
            yield sc
        yield wait(delay)


def hello_world():
    yield text("Hello World\nHow are you?", delay=0)


def macos_ss_select():
    yield KC.LEFT_UI, KC.LEFT_SHIFT
    yield KC.LEFT_UI, KC.LEFT_SHIFT, KC.N4


def macos_ss_window():
    yield from (
        macos_ss_select(),
        wait(50),
        KC.SPACE
    )


def macro_test():
    yield text("Hello World\nHow are you? <> {} [] !? @ (-_-) :D ;) £9.99 55% 7&8 1*2=2 1-1=0 One, two, three! (^ ^) 0123456789\nThe quick brown fox jumps over the lazy dog.", delay=0)
