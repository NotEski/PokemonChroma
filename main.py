from engine.pokemon.repositry_generator import initialize_repositories
from engine.pokemon.repository import pokemon_repository, ability_repository, move_repository, item_repository
from engine.battle.battle_example import pickachu_eevee_battle_example

import os

from direct.showbase.ShowBase import ShowBase


class Application(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)



initialize_repositories(os.path.dirname(os.path.abspath(__file__)))


pickachu_eevee_battle_example()









# app = Application()
# app.run()