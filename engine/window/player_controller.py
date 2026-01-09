from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .window import GameWindow

class Key(Enum):
    FORWARD = "w"
    BACK = "s"
    LEFT = "a"
    RIGHT = "d"



class PlayerController:
    game_window: "GameWindow"
    control_enabled: bool = True

    key_state: dict[Key, bool]

    def __init__(self, game_window: "GameWindow") -> None:
        self.game_window = game_window
        self.setup_controls()

    def enable_control(self) -> None:
        self.control_enabled = True
        self.game_window.disable_mouse()

    def disable_control(self) -> None:
        self.control_enabled = False
        self.game_window.enable_mouse()


    def edit_input_key(self, key: Key, new_key: str) -> None:
        Key[key.name] = new_key

        self.game_window.ignore(key.value)
        self.game_window.ignore(f"{key.value}-up")
        self.game_window.accept(new_key, self._handle_key_press, [key])
        self.game_window.accept(f"{new_key}-up", self._handle_key_release, [key])


    def _handle_key_press(self, key: Key) -> None:
        self.key_state[key] = True

    def _handle_key_release(self, key: Key) -> None:
        self.key_state[key] = False

    def setup_controls(self) -> None:
        self.key_state = {
			Key.FORWARD: False,
			Key.BACK: False,
			Key.LEFT: False,
			Key.RIGHT: False,
		}
        self.input_buffer: list[str] = []
        self.game_window.accept(Key.FORWARD.value, self._handle_key_press, [Key.FORWARD])
        self.game_window.accept(f"{Key.FORWARD.value}-up", self._handle_key_release, [Key.FORWARD])
        self.game_window.accept(Key.BACK.value, self._handle_key_press, [Key.BACK])
        self.game_window.accept(f"{Key.BACK.value}-up", self._handle_key_release, [Key.BACK])
        self.game_window.accept(Key.LEFT.value, self._handle_key_press, [Key.LEFT])
        self.game_window.accept(f"{Key.LEFT.value}-up", self._handle_key_release, [Key.LEFT])
        self.game_window.accept(Key.RIGHT.value, self._handle_key_press, [Key.RIGHT])
        self.game_window.accept(f"{Key.RIGHT.value}-up", self._handle_key_release, [Key.RIGHT])

        self.game_window.taskMgr.add(self.update_player_task, "update_player_task")

    def update_player_task(self, task) -> None:
        if self.control_enabled:
            all_false = True
            for key, value in self.key_state.items():
                if value:
                    all_false = False
            if all_false:
                return task.cont
            print (self.key_state)
        return task.cont
