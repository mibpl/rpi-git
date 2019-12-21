class KeyboardConfig:
    """
    5 octaves
    middle C == 48
    w/o transposition
        36 - 48
        48 - 60
        60 - 72
        72 - 84
        84 - 96
    """

    low_note = 36
    high_note = 96
    light_channel = 9

    def is_black_key(note):
        note = note % 12
        return note in (1, 3, 6, 8, 10)