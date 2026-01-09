"""Minimal Panda3D window that renders a stylised Pokémon-style map."""

from __future__ import annotations

import math
from typing import Optional

from panda3d.core import loadPrcFileData

# Default vsync on; can be overridden via settings panel (will trigger window reopen).
loadPrcFileData("", "sync-video true")

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import (
	DirectButton,
	DirectCheckButton,
	DirectFrame,
	DirectLabel,
	DirectOptionMenu,
)
from panda3d.core import (
	AmbientLight,
	CardMaker,
	ClockObject,
	DirectionalLight,
	Geom,
	GeomNode,
	GeomTriangles,
	GeomVertexData,
	GeomVertexFormat,
	GeomVertexWriter,
	Vec3,
	Vec4,
	WindowProperties,
)


# Coarse layout inspired by the reference image; each character maps to a solid colour tile.
MAP_LAYOUT: list[str] = [
	"BBBBBBBBBBBBBB",
	"BFFFFTTTTTFFFB",
	"BFFFTGGGGGTFFB",
	"BFFTTGGGGGTTFB",
	"BGGGGGRRRGGGGB",
	"BGGGGSRRRGGGGB",
	"BGGGGGRRRGGGGB",
	"BFFTTGGGGGTTFB",
	"BFFFTGGGGGTFFB",
	"BFFFFTTTTTFFFB",
	"BBBBBBBBBBBBBB",
]

COLOR_MAP: dict[str, Vec4] = {
	"B": Vec4(0.70, 0.80, 0.90, 1.0),  # fence / border
	"F": Vec4(0.82, 0.62, 0.36, 1.0),  # autumn foliage
	"T": Vec4(0.60, 0.75, 0.42, 1.0),  # shrubs
	"G": Vec4(0.32, 0.62, 0.28, 1.0),  # tall grass
	"R": Vec4(0.90, 0.83, 0.59, 1.0),  # dirt path
	"S": Vec4(0.75, 0.75, 0.70, 1.0),  # signpost
}

RESOLUTION_CHOICES: list[tuple[int, int]] = [
	(1280, 720),
	(1366, 768),
	(1600, 900),
	(1920, 1080),
	(2560, 1440),
]

HEIGHT_MAP: dict[str, float] = {
	"B": 0.35,
	"F": 0.50,
	"T": 0.55,
	"G": 0.60,
	"R": 0.30,
	"S": 0.65,
}


class PokemonMapWindow(ShowBase):
	def __init__(self) -> None:
		super().__init__()
		self.disableMouse()
		self.set_background_color(0.86, 0.91, 0.97, 1.0)
		if self.win is not None:
			props = WindowProperties()
			props.setTitle("Pokemon Chroma")
			self.win.requestProperties(props)
		self.setFrameRateMeter(True)
		current_props = self.win.getProperties() if self.win is not None else None
		self.settings_state = {
			"resolution": (
				current_props.getXSize() if current_props is not None else 1280,
				current_props.getYSize() if current_props is not None else 720,
			),
			"fullscreen": bool(current_props.getFullscreen()) if current_props is not None else False,
			"vsync": True,
		}
		self.map_width = 0
		self.map_height = 0
		self.tile_size = 1.0
		self.map_half_width = 0.0
		self.map_half_height = 0.0
		self.camera_vertical_offset = 0.0
		self.camera_horizontal_offset = 0.0
		self.camera_target_offset = 0.35
		self.active_move: Optional[dict[str, object]] = None
		self._setup_lighting()
		self._build_tile_map()
		self._spawn_player_billboard()
		self._configure_camera()
		self._setup_controls()
		self._build_settings_ui()
		self.accept("f1", self._toggle_settings_visibility)
		self.accept("escape", self.userExit)

	def _build_tile_map(self) -> None:
		self.map_height = len(MAP_LAYOUT)
		self.map_width = max(len(row) for row in MAP_LAYOUT)
		self.map_half_width = self.map_width * self.tile_size / 2.0
		self.map_half_height = self.map_height * self.tile_size / 2.0

		format_ = GeomVertexFormat.getV3n3c4()
		vdata = GeomVertexData("map", format_, Geom.UHStatic)
		pos_writer = GeomVertexWriter(vdata, "vertex")
		normal_writer = GeomVertexWriter(vdata, "normal")
		color_writer = GeomVertexWriter(vdata, "color")
		triangles = GeomTriangles(Geom.UHStatic)

		vertex_count = 0

		for row_index, row in enumerate(MAP_LAYOUT):
			for col_index, cell in enumerate(row):
				colour = COLOR_MAP.get(cell)
				if colour is None:
					continue

				height = HEIGHT_MAP.get(cell, 0.0)

				# Compute the four corner positions of the tile quad in the X-Y plane.
				tl_x, tl_y = self._grid_to_world(col_index, row_index)
				tr_x, tr_y = self._grid_to_world(col_index + 1, row_index)
				bl_x, bl_y = self._grid_to_world(col_index, row_index + 1)
				br_x, br_y = self._grid_to_world(col_index + 1, row_index + 1)

				corners = (
					(tl_x, tl_y),
					(bl_x, bl_y),
					(br_x, br_y),
					(tr_x, tr_y),
				)

				for x, y in corners:
					pos_writer.addData3(x, y, height)
					normal_writer.addData3(0.0, 0.0, 1.0)
					color_writer.addData4(colour)

				triangles.addVertices(vertex_count + 0, vertex_count + 1, vertex_count + 2)
				triangles.addVertices(vertex_count + 0, vertex_count + 2, vertex_count + 3)
				vertex_count += 4

		geom = Geom(vdata)
		geom.addPrimitive(triangles)
		geom_node = GeomNode("map-node")
		geom_node.addGeom(geom)
		self.map_np = self.render.attachNewNode(geom_node)

	def _grid_to_world(self, col: float, row: float) -> tuple[float, float]:
		x = (col - self.map_width / 2.0) * self.tile_size
		y = (self.map_height / 2.0 - row) * self.tile_size
		return x, y

	def _spawn_player_billboard(self) -> None:
		position = self._find_player_spawn()
		maker = CardMaker("player")
		maker.setFrame(-0.25, 0.25, 0.0, 0.8)
		player_card = maker.generate()
		self.player_np = self.render.attachNewNode(player_card)
		self.player_np.setPos(position)
		self.player_np.setBillboardPointEye()
		self.player_np.setColor(Vec4(0.20, 0.25, 0.65, 1.0))

	def _find_player_spawn(self) -> Vec3:
		for row_index, row in enumerate(MAP_LAYOUT):
			for col_index, cell in enumerate(row):
				if cell == "R":
					center_x, center_y = self._grid_to_world(
						col_index + 0.5,
						row_index + 0.5,
					)
					height = HEIGHT_MAP.get(cell, 0.0)
					return Vec3(center_x, center_y, height + 0.05)

		return Vec3(0.0, 0.0, 0.35)

	def _configure_camera(self) -> None:
		largest_dim = float(max(self.map_width, self.map_height))

		self.camera_vertical_offset = largest_dim * 0.9
		self.camera_horizontal_offset = self.camera_vertical_offset * math.tan(math.radians(25.0))
		self._update_camera_position()
		self.camLens.setFov(55.0)

	def _update_camera_position(self) -> None:
		player_pos = self.player_np.getPos()
		self.camera.setPos(
			player_pos.x,
			player_pos.y - self.camera_horizontal_offset,
			player_pos.z + self.camera_vertical_offset,
		)
		self.camera.lookAt(player_pos.x, player_pos.y, player_pos.z + self.camera_target_offset)

	def _setup_controls(self) -> None:
		self.key_state: dict[str, bool] = {
			"forward": False,
			"back": False,
			"left": False,
			"right": False,
		}
		self.input_buffer: list[str] = []
		self.accept("w", self._handle_key_press, ["forward"])
		self.accept("w-up", self._handle_key_release, ["forward"])
		self.accept("s", self._handle_key_press, ["back"])
		self.accept("s-up", self._handle_key_release, ["back"])
		self.accept("a", self._handle_key_press, ["left"])
		self.accept("a-up", self._handle_key_release, ["left"])
		self.accept("d", self._handle_key_press, ["right"])
		self.accept("d-up", self._handle_key_release, ["right"])
		self.move_duration = 0.12
		self.taskMgr.add(self._update_player_task, "update-player")

	def _build_settings_ui(self) -> None:
		self.settings_frame = DirectFrame(
			frameColor=(0, 0, 0, 0.7),
			frameSize=(-0.7, 0.7, -0.5, 0.5),
			pos=(0, 0, 0),
			parent=self.aspect2d,
		)

		DirectLabel(
			text="Video Settings (F1)",
			scale=0.07,
			pos=(-0.65, 0, 0.38),
			parent=self.settings_frame,
		)

		DirectLabel(
			text="Resolution",
			scale=0.05,
			pos=(-0.65, 0, 0.2),
			parent=self.settings_frame,
		)
		res_labels = [f"{w}x{h}" for w, h in RESOLUTION_CHOICES]
		initial_label = f"{self.settings_state['resolution'][0]}x{self.settings_state['resolution'][1]}"
		initial_index = res_labels.index(initial_label) if initial_label in res_labels else 0
		self.res_menu = DirectOptionMenu(
			text="",
			scale=0.05,
			items=res_labels,
			initialitem=initial_index,
			pos=(-0.05, 0, 0.2),
			parent=self.settings_frame,
			command=self._on_resolution_select,
		)

		self.fullscreen_check = DirectCheckButton(
			text="Fullscreen",
			scale=0.05,
			pos=(-0.65, 0, 0.02),
			parent=self.settings_frame,
			indicatorValue=self.settings_state["fullscreen"],
			command=self._on_fullscreen_toggle,
		)

		self.vsync_check = DirectCheckButton(
			text="VSync",
			scale=0.05,
			pos=(-0.65, 0, -0.12),
			parent=self.settings_frame,
			indicatorValue=self.settings_state["vsync"],
			command=self._on_vsync_toggle,
		)

		DirectButton(
			text="Uncap FPS",
			scale=0.045,
			pos=(0.15, 0, -0.12),
			parent=self.settings_frame,
			command=self._uncap_fps,
		)

		DirectButton(
			text="Apply",
			scale=0.05,
			pos=(-0.4, 0, -0.32),
			parent=self.settings_frame,
			command=self._apply_video_settings,
		)

		DirectButton(
			text="Close",
			scale=0.05,
			pos=(0.2, 0, -0.32),
			parent=self.settings_frame,
			command=self._toggle_settings_visibility,
		)

		DirectLabel(
			text="Apply recreates the window to change vsync/fullscreen.",
			scale=0.04,
			pos=(-0.65, 0, -0.42),
			parent=self.settings_frame,
		)

		self.settings_frame.hide()

	def _handle_key_press(self, key: str) -> None:
		self.key_state[key] = True
		if key not in self.input_buffer:
			self.input_buffer.append(key)

	def _handle_key_release(self, key: str) -> None:
		self.key_state[key] = False
		if key in self.input_buffer:
			self.input_buffer.remove(key)

	def _toggle_settings_visibility(self) -> None:
		if self.settings_frame.isHidden():
			self._refresh_settings_controls()
			self.settings_frame.show()
		else:
			self.settings_frame.hide()

	def _update_player_task(self, task) -> int:
		dt = ClockObject.getGlobalClock().get_dt()

		if self.active_move is not None:
			self.active_move["elapsed"] = float(self.active_move.get("elapsed", 0.0)) + dt
			start: Vec3 = self.active_move["start"]  # type: ignore[assignment]
			end: Vec3 = self.active_move["end"]  # type: ignore[assignment]
			duration: float = float(self.active_move.get("duration", self.move_duration))
			t = min(1.0, self.active_move["elapsed"] / duration)
			new_pos = start + (end - start) * t
			self.player_np.setPos(new_pos)
			if t >= 1.0 - 1e-5:
				self.player_np.setPos(end)
				self.active_move = None
		else:
			direction = self._resolve_direction()
			if direction is not None:
				dx, dy = direction
				self._start_step(dx, dy)

		self._update_camera_position()
		return task.cont

	def _resolve_direction(self) -> tuple[int, int] | None:
		for key in reversed(self.input_buffer):
			if self.key_state.get(key, False):
				if key == "forward":
					return (0, 1)
				if key == "back":
					return (0, -1)
				if key == "left":
					return (-1, 0)
				if key == "right":
					return (1, 0)
		return None

	def _refresh_settings_controls(self) -> None:
		res_labels = [f"{w}x{h}" for w, h in RESOLUTION_CHOICES]
		target_label = f"{self.settings_state['resolution'][0]}x{self.settings_state['resolution'][1]}"
		if target_label in res_labels:
			self.res_menu.set(res_labels.index(target_label))
		self.fullscreen_check["indicatorValue"] = self.settings_state["fullscreen"]
		self.fullscreen_check.setIndicatorValue()
		self.vsync_check["indicatorValue"] = self.settings_state["vsync"]
		self.vsync_check.setIndicatorValue()

	def _start_step(self, grid_dx: int, grid_dy: int) -> bool:
		if self.active_move is not None:
			return False

		current_pos = self.player_np.getPos()
		target_x = current_pos.x + grid_dx * self.tile_size
		target_y = current_pos.y + grid_dy * self.tile_size
		target_x = self._clamp(target_x, -self.map_half_width + 0.5 * self.tile_size, self.map_half_width - 0.5 * self.tile_size)
		target_y = self._clamp(target_y, -self.map_half_height + 0.5 * self.tile_size, self.map_half_height - 0.5 * self.tile_size)
		if abs(target_x - current_pos.x) < 1e-5 and abs(target_y - current_pos.y) < 1e-5:
			return False
		target_z = self._sample_height(target_x, target_y) + 0.05
		end_pos = Vec3(target_x, target_y, target_z)

		self.active_move = {
			"start": current_pos,
			"end": end_pos,
			"elapsed": 0.0,
			"duration": self.move_duration,
		}
		return True

	def _on_resolution_select(self, selection: str) -> None:
		if "x" in selection:
			parts = selection.split("x")
			if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
				self.settings_state["resolution"] = (int(parts[0]), int(parts[1]))

	def _on_fullscreen_toggle(self, state: bool) -> None:
		self.settings_state["fullscreen"] = bool(state)

	def _on_vsync_toggle(self, state: bool) -> None:
		self.settings_state["vsync"] = bool(state)

	def _uncap_fps(self) -> None:
		self.settings_state["vsync"] = False
		self.vsync_check["indicatorValue"] = False
		self.vsync_check.setIndicatorValue()
		self._apply_video_settings()

	def _apply_video_settings(self) -> None:
		if self.win is None:
			return
		props = WindowProperties()
		props.setTitle("Pokemon Chroma")
		props.setFullscreen(self.settings_state.get("fullscreen", False))
		res = self.settings_state.get("resolution", (1280, 720))
		props.setSize(int(res[0]), int(res[1]))
		vsync_enabled = self.settings_state.get("vsync", True)
		if hasattr(WindowProperties, "setSyncVideo"):
			props.setSyncVideo(vsync_enabled)
		else:
			loadPrcFileData("", f"sync-video {'true' if vsync_enabled else 'false'}")
		self.win.requestProperties(props)
		updated = self.win.getProperties()
		self.settings_state["resolution"] = (updated.getXSize(), updated.getYSize())
		self.settings_state["fullscreen"] = bool(updated.getFullscreen())
		# setSyncVideo does not expose getter; keep requested value

	def _sample_height(self, x: float, y: float) -> float:
		col = int(math.floor(x / self.tile_size + self.map_width / 2.0))
		row = int(math.floor(self.map_height / 2.0 - y / self.tile_size))
		col = self._clamp_int(col, 0, self.map_width - 1)
		row = self._clamp_int(row, 0, self.map_height - 1)
		cell = MAP_LAYOUT[row][col]
		return HEIGHT_MAP.get(cell, 0.0)

	@staticmethod
	def _clamp(value: float, minimum: float, maximum: float) -> float:
		return max(minimum, min(value, maximum))

	@staticmethod
	def _clamp_int(value: int, minimum: int, maximum: int) -> int:
		return max(minimum, min(value, maximum))

	def _setup_lighting(self) -> None:
		ambient = AmbientLight("ambient")
		ambient.setColor(Vec4(0.55, 0.60, 0.65, 1.0))
		ambient_np = self.render.attachNewNode(ambient)
		self.render.setLight(ambient_np)

		sun = DirectionalLight("sun")
		sun.setColor(Vec4(0.95, 0.90, 0.80, 1.0))
		sun_np = self.render.attachNewNode(sun)
		sun_np.setHpr(-35.0, -50.0, 0.0)
		self.render.setLight(sun_np)

def main() -> None:
	app = PokemonMapWindow()
	app.run()


if __name__ == "__main__":
	main()

