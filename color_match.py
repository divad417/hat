import time
import random
import displayio
import terminalio
from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect
from adafruit_bitmap_font import bitmap_font

# arial_60 = bitmap_font.load_font('/fonts/arial-60.bdf')
# arial_200 = bitmap_font.load_font('/fonts/arial-200.bdf')

def read_button(neokey, index):
    """Speedup to neokey __getitem__ method."""
    return not neokey.digital_read_bulk(1 << (index + 4), delay=0)


class ColorMatch:

    def __init__(self, hat):
        self.keypads = hat.keypads
        self.display = hat.display
        self.leds = hat.leds

        # Setup display objects
        self.score_text_group = displayio.Group(x=120, y=160)
        self.score_text_group.hidden = True
        hat.splash.append(self.score_text_group)
        for i in range(2):
            text = Label(terminalio.FONT, text='0', color=0xFFFFFF, scale=8)
            text.anchor_point = 0.5, 0.5
            text.anchored_position = i*240, 0
            self.score_text_group.append(text)

        self.ready_flasher_group = displayio.Group(x=120, y=155)
        self.ready_flasher_group.hidden = True
        hat.splash.append(self.ready_flasher_group)
        for i in range(6):
            rect = Rect(i*48, 0, 10, 10, fill=0xFFFFFF)
            self.ready_flasher_group.append(rect)

        self.color_text = Label(terminalio.FONT, text='', color=0x000000, scale=5)
        self.color_text.anchor_point = 0.5, 0.5
        self.color_text.anchored_position = 0, 0
        self.color_text_group = displayio.Group(x=240, y=160)
        self.color_text_group.hidden = True
        self.color_text_group.append(self.color_text)
        hat.splash.append(self.color_text_group)



    def all_off(self):
        for keypad in self.keypads:
            keypad.pixels.fill(0x000000)
            keypad.pixels.show()
        self.leds.fill(0)
        self.leds.show()

    def all_on(self):
        for keypad in self.keypads:
            keypad.pixels.fill(0x777777)
            keypad.pixels.show()
        self.leds.fill(0xFFFFFF)
        self.leds.show()

    def wait_for_input(self):
        keypads = self.keypads
        while True:
            for player, keypad in enumerate(keypads):
                for i in range(4):
                    # if read_button(keypad, i):
                    if not keypad.digital_read_bulk(1 << (i + 4), delay=0.001):
                        return player, i

    def show_scoreboard(self, duration, faster_player=None, correct=None):
        leds = ((14, 15, 16, 17), (1, 2, 3, 4))
        for score, text in zip(self.score, self.score_text_group):
            text.text = str(score)
        if faster_player is not None:
            self.score_text_group[faster_player].color = 0x00FF00 if correct else 0xFF0000
            for i in leds[faster_player]:
                self.leds[i] = 0x00FF00 if correct else 0xFF0000
                self.leds.show()
        # Update score display objects text and color
        self.score_text_group.hidden = False
        self.display.refresh()
        time.sleep(duration)
        self.score_text_group.hidden = True
        for text in self.score_text_group:
            text.color = 0xFFFFFF
        self.leds.fill(0)
        self.display.refresh()
        self.leds.show()

    def ready_flasher(self, number, duration):
        for i in range(number):
            self.ready_flasher_group.hidden = False
            self.all_on()
            self.display.refresh()
            time.sleep(duration)
            self.ready_flasher_group.hidden = True
            self.all_off()
            self.display.refresh()
            time.sleep(duration)

    def round(self):
        color_dict = {
            'Red': 0xFF0000,
            'Orange': 0xFF3F00,
            'Yellow': 0xFFCF00,
            'Green': 0x00FF00,
            'Cyan': 0x00FF7F,
            'Blue': 0x0000FF,
            'Purple': 0xAF00FF,
        }

        # Select main color
        round_colors = sorted(color_dict, key=lambda _: random.random())
        color_win = round_colors[0]
        color_show = round_colors[1]
        round_colors = sorted(round_colors[0:4], key=lambda _: random.random())

        self.color_text.text = color_win
        self.color_text.color = color_dict[color_show]
        self.color_text_group.hidden = False

        for keypad in self.keypads:
            for i, color in enumerate(round_colors):
                keypad.pixels[i] = color_dict[color]
        for keypad in self.keypads:
            keypad.pixels.show()
        for i in range(len(self.leds)):
            self.leds[i] = color_dict[color_show]
        self.leds.show()
        self.display.refresh()

        # Play the game
        player, idx = self.wait_for_input()

        correct = round_colors[idx] == color_win
        if correct:
            self.score[player] +=1
        else:
            self.score[(player+1)%2] +=1

        self.all_off()
        self.keypads[player].pixels[idx] = color_dict[round_colors[idx]]
        self.keypads[player].pixels.show()
        self.color_text_group.hidden = True
        self.display.refresh()

        # Increment score
        return player, correct

    def show_winner(self):
        offset = 360 if self.score[1] > self.score[0] else 120
        leds = ((14, 15, 16, 17), (1, 2, 3, 4))
        self.color_text.text = 'WINNER!'
        self.color_text.color = 0xFFFFFF
        self.color_text_group.x = offset
        self.color_text_group.hidden = False
        self.display.refresh()
        for i in leds[self.score[1] > self.score[0]]:
            self.leds[i] = 0xFFFFFF
        self.leds.show()
        time.sleep(10)
        self.color_text_group.hidden = True
        self.color_text_group.x = 240
        self.all_off()
        self.display.refresh()

    def play(self):
        self.score = [0, 0]
        faster_player = None
        correct = None

        while max(self.score) <= 4:
            self.show_scoreboard(3.5, faster_player, correct)
            self.ready_flasher(random.randint(2, 9), 0.135)
            faster_player, correct = self.round()

        self.show_winner()
