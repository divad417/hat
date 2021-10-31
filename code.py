import hat
from color_match import ColorMatch
from menu import Menu

menu = Menu(hat)
game = ColorMatch(hat)
menu.add_game(game)

while True:
    game = menu.show()
    game.play()

