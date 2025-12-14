import pyglet


# Query the best config for the screen
display = pyglet.display.get_display()
screen = display.get_default_screen()
config = screen.get_best_config()


window =  pyglet.window.Window(config=config,
                               resizable=True,
                               width=800,
                               height=600,
                               caption='Pokemon Game')

label = pyglet.text.Label('Hello, Pyglet!',
                            font_name='Comic Sans MS',
                            color=(255, 255, 255, 255),
                            font_size=36,
                            x=window.width//2, y=window.height//2,
                            anchor_x='center', anchor_y='center')

eevee_image = pyglet.image.load(".\\assets\\0133-Eevee\\static.png")

@window.event
def on_draw():
    window.clear()
    label.draw()
    eevee_image.blit(100, 100)

@window.event
def on_resize(width, height):
    pass



def game_window():
    pyglet.app.run()