import pyxel

pyxel.init(450,300, title="our game")
class App:
    def __init__(self):
        self.x = 0
        self.y = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= 1
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += 1
        if pyxel.btn(pyxel.KEY_UP):
            self.y -= 1
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += 1

    def draw(self):
        pyxel.cls(0)
        pyxel.rect(self.x, self.y, 10, 10, 11)
App()