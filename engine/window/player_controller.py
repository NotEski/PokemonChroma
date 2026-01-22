from typing import TYPE_CHECKING
from enum import Enum

from pydantic import BaseModel
from direct.task.Task import Task

if TYPE_CHECKING:
    from .window import GameWindow

class Direction(Enum):
    FORWARD = "forward"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"

class Keybinds(BaseModel):
    forward: str = "w"
    back: str = "s"
    left: str = "a"
    right: str = "d"


class PlayerController:
    game_window: "GameWindow"
    control_enabled: bool = True

    direction_key_state: dict[Direction, bool]
    keybinds: Keybinds

    def __init__(self, game_window: "GameWindow") -> None:
        self.game_window = game_window
        self.keybinds = Keybinds()
        self.setup_controls()

    def enable_control(self) -> None:
        self.control_enabled = True
        self.game_window.disable_mouse()

    def disable_control(self) -> None:
        self.control_enabled = False
        self.game_window.enable_mouse()


    def edit_input_key(self, key: str, new_key: str) -> None:
        if not hasattr(self.keybinds, key.lower()):
            return
        setattr(self.keybinds, key.lower(), new_key)

        self.game_window.ignore(getattr(self.keybinds, key.lower()))
        self.game_window.ignore(f"{getattr(self.keybinds, key.lower())}-up")
        self.game_window.accept(new_key, self._handle_key_press, [Direction[key.upper()]])
        self.game_window.accept(f"{new_key}-up", self._handle_key_release, [Direction[key.upper()]])


    def _handle_key_press(self, key: Direction) -> None:
        self.direction_key_state[key] = True

    def _handle_key_release(self, key: Direction) -> None:
        self.direction_key_state[key] = False

    def setup_controls(self) -> None:
        self.direction_key_state = {
			Direction.FORWARD: False,
			Direction.BACK: False,
			Direction.LEFT: False,
			Direction.RIGHT: False,
		}
        self.input_buffer: list[str] = []
        self.game_window.accept(self.keybinds.forward, self._handle_key_press, [Direction.FORWARD])
        self.game_window.accept(f"{self.keybinds.forward}-up", self._handle_key_release, [Direction.FORWARD])
        self.game_window.accept(self.keybinds.back, self._handle_key_press, [Direction.BACK])
        self.game_window.accept(f"{self.keybinds.back}-up", self._handle_key_release, [Direction.BACK])
        self.game_window.accept(self.keybinds.left, self._handle_key_press, [Direction.LEFT])
        self.game_window.accept(f"{self.keybinds.left}-up", self._handle_key_release, [Direction.LEFT])
        self.game_window.accept(self.keybinds.right, self._handle_key_press, [Direction.RIGHT])
        self.game_window.accept(f"{self.keybinds.right}-up", self._handle_key_release, [Direction.RIGHT])

        self.game_window.taskMgr.add(self.update_player_task, "update_player_task")

    def update_player_task(self, task: Task) -> int:
        if self.control_enabled:
            all_false = True
            for _, value in self.direction_key_state.items():
                if value:
                    all_false = False
            if all_false:
                return task.cont
            print (self.direction_key_state)
        return task.cont
