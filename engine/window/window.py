from typing import Optional

from engine.main import application_root

from direct.showbase.ShowBase import ShowBase

from panda3d.core import (
    WindowProperties
)

from engine.repositories.repositry_generator import initialize_repositories

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
        if self.win is not None: # type: ignore 
            return True
        return False

    def set_window_title(self, title: str) -> None:
        if not self.get_win(): return None
        props = WindowProperties()
        props.setTitle(title)
        self.win.requestProperties(props) # type: ignore

    def set_window_size(self, width: int, height: int) -> None:
        if not self.get_win(): return None
        props = WindowProperties()
        props.setSize(width, height)
        self.win.requestProperties(props) # type: ignore

    def get_window_size(self) -> Optional[tuple[int, int]]:
        if not self.get_win(): return None
        props = self.win.getProperties() # type: ignore
        x_size: int = int(props.getXSize()) # type: ignore
        y_size: int = int(props.getYSize()) # type: ignore
        return (x_size, y_size)

    def disable_mouse(self) -> None:
        self.disableMouse()

    def enable_mouse(self) -> None:
        self.enableMouse()

    @property
    def is_mouse_enabled(self) -> bool:
        return self.mouseWatcherNode.hasMouse()



def launch_game_window() -> None:
	app = GameWindow()
	app.run()


if __name__ == "__main__":
	launch_game_window()