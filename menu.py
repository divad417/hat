import displayio
import terminalio
import rainbowio
import time
from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect

def touch_transform(point):
    y = (4096 - point[0])*320/4096
    x = point[1]*480/4096
    return int(x), int(y)

class Menu:
    def __init__(self, hat):
        self.display = hat.display
        self.touch = hat.touch
        self.leds = hat.leds
        self.backlight = hat.backlight

        rect = Rect(120, 110, 240, 100, outline=0xFFFFFF)
        label = Label(terminalio.FONT, text='Play!', color=0xFFFFFF, scale=4)
        label.anchor_point = 0.5, 0.5
        label.anchored_position = 240, 160
        self.group = displayio.Group()
        self.group.append(rect)
        self.group.append(label)
        hat.splash.append(self.group)

    def add_game(self, game):
        self.game = game

    def empty_touch_buffer(self):
        while not self.touch.buffer_empty:
            self.touch.read_data()

    def show(self):
        idx = 0
        color = 0
        enabled = True

        self.group.hidden = False
        self.display.refresh()
        self.empty_touch_buffer()

        while True:
            if not self.touch.buffer_empty:
                x, y = touch_transform(self.touch.read_data())
                if enabled and 120 < x < 360 and 110 < y < 210:
                    self.group.hidden = True
                    self.display.refresh()
                    break
                enabled = not enabled
                self.backlight.value = enabled
                time.sleep(0.2)
                self.empty_touch_buffer()

            if enabled:
                self.leds[idx] = rainbowio.colorwheel(color)
                self.leds[idx+9] = rainbowio.colorwheel(color)
                self.leds.show()

                time.sleep(0.05)

                self.leds[idx] = 0
                self.leds[idx+9] = 0
                self.leds.show()

                idx = (idx + 1) % 9
                color = (color + 1) % 256
        self.leds.fill(0)
        self.backlight.value = True

        return self.game
