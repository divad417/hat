import board
import digitalio
import displayio
import neopixel
from adafruit_hx8357 import HX8357
from adafruit_neokey.neokey1x4 import NeoKey1x4
from adafruit_stmpe610 import Adafruit_STMPE610_SPI

auto_refresh = False

displayio.release_displays()

spi = board.SPI()
i2c = board.I2C()

sd_cs = board.D5
touch_cs = digitalio.DigitalInOut(board.D6)
led_pin = board.D12
led_n = 18
display_cs = board.D9
display_dc = board.D10

# Display
display_bus = displayio.FourWire(spi, command=display_dc, chip_select=display_cs)
display = HX8357(display_bus, width=480, height=320, rotation=180, auto_refresh=auto_refresh)
touch = Adafruit_STMPE610_SPI(spi, touch_cs)
# Display backlight
backlight = digitalio.DigitalInOut(board.D11)
backlight.direction = digitalio.Direction.OUTPUT
backlight.value = True
# Top level displayio Group
splash = displayio.Group()
display.show(splash)

# Input keys
keypads = (NeoKey1x4(i2c, addr=0x30), NeoKey1x4(i2c, addr=0x31))
for keypad in keypads:
    keypad.pixels.auto_write = auto_refresh
    keypad.pixels.fill(0)

# Ring lights on top of the hat
leds = neopixel.NeoPixel(board.D12, led_n, pixel_order=neopixel.GRBW, auto_write=auto_refresh)
leds.brightness = 0.1
leds.fill(0)

def refresh():
    """Update all outputs, for use when auto_refresh is False."""
    display.refresh()
    for keypad in keypads:
        keypad.pixels.show()
    leds.show()

if not auto_refresh:
    refresh()
