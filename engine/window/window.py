from typing import Optional

from engine.main import application_root

from direct.showbase.ShowBase import ShowBase

from panda3d.core import (
    Geom,
    WindowProperties
)

from engine.pokemon.repositry_generator import initialize_repositories

from .player_controller import PlayerController


from panda3d.core import loadPrcFileData
loadPrcFileData("", "sync-video false")


class GameWindow(ShowBase):
    def __init__(self) -> None:
        super().__init__()
        self.set_background_color(0.86, 0.91, 0.97, 1.0)
        self.set_window_title("Pokemon Chroma")
        self.set_window_size(1920, 1080)
        self.setFrameRateMeter(True)

        self.player_controller: PlayerController = PlayerController(self)
        self.player_controller.enable_control()

        self.accept("escape", self.userExit)

        initialize_repositories(application_root)

    def get_win(self) -> bool:
        if self.win is not None: 
            return True
        return False

    def set_window_title(self, title: str) -> None:
        if not self.get_win(): return None
        props = WindowProperties()
        props.setTitle(title)
        self.win.requestProperties(props)

    def set_window_size(self, width: int, height: int) -> None:
        if not self.get_win(): return None
        props = WindowProperties()
        props.setSize(width, height)
        self.win.requestProperties(props)

    def get_window_size(self) -> Optional[tuple[int, int]]:
        if not self.get_win(): return None
        props = self.win.getProperties()
        return (props.getXSize(), props.getYSize())

    def disable_mouse(self) -> None:
        self.disableMouse()

    def enable_mouse(self) -> None:
        self.enableMouse()



def launch_game_window() -> None:
	app = GameWindow()
	app.run()


if __name__ == "__main__":
	launch_game_window()