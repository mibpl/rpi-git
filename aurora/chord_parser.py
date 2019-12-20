import pychord
import sys

def parse_song(text):
    chords = []
    for token in text.split():
        try:
            chords.append(pychord.Chord(token))
        except ValueError:
            pass
    return chords

if __name__ == '__main__':
    print(parse_song("\n".join(sys.stdin.readlines())))