from engine.pokemon.repositry_generator import initialize_repositories
from engine.pokemon.repository import pokemon_repository, move_repository, item_repository, ability_repository, status_repository, hazard_repository
from engine.battle.battle_example import moveset_from_names
from engine.battle.battle_manager import BattleManager
from shared.battle.position_manager import BattlePosition
from shared.battle.opponent import TrainerOpponent
from shared.trainer.trainer import Trainer
from shared.pokemon.pokemon import PokemonTeam, Pokemon
from shared.battle.battle_actions import MoveAction

import os
import traceback
import tkinter as tk
from tkinter import ttk

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


# Tkinter battle inspector helpers


def simulate_sample_battle():
    pikachu_moveset = moveset_from_names(["toxic_spikes", "growl", "volt_tackle", "quick_attack"])
    eevee_moveset = moveset_from_names(["tackle", "tail_whip", "bite", "quick_attack"])

    pikachu_base = pokemon_repository.get("pikachu")
    eevee_base = pokemon_repository.get("eevee")

    pikachu = Pokemon(pokemon_base=pikachu_base, level=50, move_set=pikachu_moveset)
    pikachu.nickname = "Pickle"
    pikachu.held_item = item_repository.get("light_ball")


    eevee = Pokemon(pokemon_base=eevee_base, level=50, move_set=eevee_moveset)
    eevee.nickname = "Stevie"
    eevee.held_item = item_repository.get("eviolite")


    marshtomp_moveset = moveset_from_names(["mud_slap", "water_gun", "rock_throw", "protect"])
    marshtomp_base = pokemon_repository.get("marshtomp")
    marshtomp = Pokemon(pokemon_base=marshtomp_base, level=50, move_set=marshtomp_moveset)
    

    youngseos_team = PokemonTeam(pokemons=[pikachu])
    trainer_1 = Trainer(name="Youngseo", team=youngseos_team)
    
    declans_team = PokemonTeam(pokemons=[marshtomp])
    trainer_2 = Trainer(name="Declan", team=declans_team)

    opponent_1 = TrainerOpponent(trainer=trainer_1)
    opponent_2 = TrainerOpponent(trainer=trainer_2)

    battle_manager = BattleManager(teams=[opponent_1, opponent_2])
    battle_manager.init_battle()
    battle_manager.start_turn()

    return battle_manager, opponent_1, opponent_2


class BattleInspectorWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pokemon Chroma Battle Inspector")
        self.root.geometry("1080x720")

        # Print full tracebacks to terminal for Tkinter callback errors
        def _tk_exception_printer(exc, val, tb):
            print("[Tkinter] Exception in callback:")
            traceback.print_exception(exc, val, tb)

        self.root.report_callback_exception = _tk_exception_printer

        self.turn_label = None
        self.team_frames = {}
        self.log_box = None
        self.opponents = {}
        self.battle_manager = None

        self._build_layout()
        self.refresh()

    def _build_layout(self):
        header = ttk.Label(self.root, text="Battle Inspector", font=("Segoe UI", 16, "bold"))
        header.pack(pady=6)

        controls = ttk.Frame(self.root)
        controls.pack(fill="x", padx=10)
        ttk.Button(controls, text="Re-run sample battle", command=self.refresh).pack(side="left")
        ttk.Button(controls, text="End Turn", command=self.end_turn).pack(side="left", padx=(8, 0))
        self.turn_label = ttk.Label(controls, text="")
        self.turn_label.pack(side="left", padx=12)

        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True, padx=10, pady=10)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.columnconfigure(2, weight=2)
        body.rowconfigure(0, weight=1)

        self.team_frames[1] = self._build_team_panel(body, "Team 1", column=0)
        self.team_frames[2] = self._build_team_panel(body, "Team 2", column=1)

        log_frame = ttk.LabelFrame(body, text="Battle Log")
        log_frame.grid(row=0, column=2, sticky="nsew", padx=8)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.log_box = tk.Text(log_frame, height=20, state="disabled", wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=scrollbar.set)
        self.log_box.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _build_team_panel(self, parent, title: str, column: int):
        frame = ttk.LabelFrame(parent, text=title)
        frame.grid(row=0, column=column, sticky="nsew", padx=8)
        frame.columnconfigure(0, weight=1)

        trainer_label = ttk.Label(frame, text="Trainer: -", font=("Segoe UI", 10, "bold"))
        trainer_label.grid(row=0, column=0, sticky="w", pady=(4, 0))

        name_label = ttk.Label(frame, text="Pokemon: -", font=("Segoe UI", 11))
        name_label.grid(row=1, column=0, sticky="w")

        hp_canvas = tk.Canvas(frame, width=240, height=22, highlightthickness=1, highlightbackground="#888")
        hp_canvas.grid(row=2, column=0, sticky="w", pady=4)
        hp_text = ttk.Label(frame, text="HP: -/-")
        hp_text.grid(row=3, column=0, sticky="w")

        status_label = ttk.Label(frame, text="Status: none")
        status_label.grid(row=4, column=0, sticky="w", pady=(2, 6))

        moves_label = ttk.Label(frame, text="Moves")
        moves_label.grid(row=5, column=0, sticky="w")
        moves_list = tk.Listbox(frame, height=6)
        moves_list.grid(row=6, column=0, sticky="nsew", pady=(0, 6))
        frame.rowconfigure(6, weight=1)

        move_var = tk.StringVar()
        move_selector = ttk.Combobox(frame, textvariable=move_var, state="readonly")
        move_selector.grid(row=7, column=0, sticky="ew", pady=(0, 4))
        queue_button = ttk.Button(frame, text="Queue Move")
        queue_button.grid(row=8, column=0, sticky="ew", pady=(0, 6))

        burn_button = ttk.Button(frame, text="Give Burn")
        burn_button.grid(row=9, column=0, sticky="ew", pady=(0, 6))

        queued_label = ttk.Label(frame, text="Queued: none")
        queued_label.grid(row=10, column=0, sticky="w")

        return {
            "frame": frame,
            "trainer": trainer_label,
            "name": name_label,
            "hp_canvas": hp_canvas,
            "hp_text": hp_text,
            "status": status_label,
            "moves": moves_list,
            "move_var": move_var,
            "move_selector": move_selector,
            "queue_button": queue_button,
            "burn_button": burn_button,
            "queued_label": queued_label,
        }

    def _draw_hp_bar(self, canvas: tk.Canvas, current: int, maximum: int):
        canvas.delete("all")
        width = int(canvas["width"])
        height = int(canvas["height"])
        canvas.create_rectangle(0, 0, width, height, outline="#444")
        if maximum <= 0:
            return
        ratio = max(0.0, min(1.0, current / maximum))
        fill_width = int(width * ratio)
        color = "#4caf50" if ratio > 0.5 else ("#ffc107" if ratio > 0.2 else "#f44336")
        canvas.create_rectangle(0, 0, fill_width, height, fill=color, width=0)

    def _format_status(self, pokemon) -> str:
        # Supports either BattleMon or Pokemon with an attached battlemon
        statuses_dict = None
        if hasattr(pokemon, "status_conditions"):
            statuses_dict = pokemon.status_conditions
        elif hasattr(pokemon, "battlemon") and pokemon.battlemon is not None and hasattr(pokemon.battlemon, "status_conditions"):
            statuses_dict = pokemon.status_conditions

        statuses = list(statuses_dict.keys()) if statuses_dict else []
        if not statuses:
            return "Status: none"
        names = ", ".join([getattr(s, "name", str(s)) for s in statuses])
        return f"Status: {names}"

    def _format_moves(self, moves_listbox: tk.Listbox, move_selector: ttk.Combobox, move_var: tk.StringVar, pokemon):
        moves_listbox.delete(0, tk.END)
        move_names = []
        for move in pokemon.move_set.moves.values():
            display = f"{move.name}  PP {move.current_pp}/{move.pp}"
            moves_listbox.insert(tk.END, display)
            move_names.append(move.name)
        move_selector["values"] = move_names
        if move_names:
            move_var.set(move_names[0])

    def _update_panel(self, panel_widgets: dict, pokemon, owner_label: str, position: BattlePosition):
        panel_widgets["trainer"].config(text=f"Trainer: {owner_label}")
        if pokemon is None:
            panel_widgets["name"].config(text="Pokemon: -")
            panel_widgets["hp_text"].config(text="HP: -/-")
            panel_widgets["status"].config(text="Status: none")
            panel_widgets["moves"].delete(0, tk.END)
            self._draw_hp_bar(panel_widgets["hp_canvas"], 0, 1)
            panel_widgets["queued_label"].config(text="Queued: none")
            return

        base_name = getattr(pokemon.pokemon_base, "display_name", None) or getattr(pokemon.pokemon_base, "name", "-")
        panel_widgets["name"].config(text=f"Pokemon: {pokemon.nickname} (Lv {pokemon.level}) [{base_name}]")
        panel_widgets["hp_text"].config(text=f"HP: {pokemon.current_hp}/{pokemon.max_hp}")
        panel_widgets["status"].config(text=self._format_status(pokemon))
        self._draw_hp_bar(panel_widgets["hp_canvas"], pokemon.current_hp, pokemon.max_hp)
        self._format_moves(panel_widgets["moves"], panel_widgets["move_selector"], panel_widgets["move_var"], pokemon)

        action = self.battle_manager.position_manager.get_position_action(position)
        if action:
            action_name = getattr(action, "move_index", None)
            if action_name is not None:
                move_obj = pokemon.move_set.moves.get(action.move_index)
                if move_obj:
                    panel_widgets["queued_label"].config(text=f"Queued: {move_obj.name}")
                    return
            panel_widgets["queued_label"].config(text="Queued: action set")
        else:
            panel_widgets["queued_label"].config(text="Queued: none")

    def _format_log_line(self, log):
        prefix = f"[{log.log_type.value}]\n" if hasattr(log, "log_type") else ""
        if getattr(log, "description", ""):
            return prefix + log.description
        turn_no = getattr(log, "turn_number", None)
        if turn_no is not None:
            return f"{prefix}Turn {turn_no} started"
        return prefix + "No description provided"

    def _render_logs(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", tk.END)
        for log in self.battle_manager.battle_log.logs:
            self.log_box.insert(tk.END, self._format_log_line(log) + "\n")
        self.log_box.configure(state="disabled")

    def _render_state(self):
        self.turn_label.config(text=f"Turn counter: {self.battle_manager.battle_state.turn_number}")
        positions = self.battle_manager.position_manager.list_registered_positions()
        for position in positions:
            pokemon = self.battle_manager.position_manager.get_pokemon_at_position(position)
            owner = self._owner_name(position.team_id)
            panel = self.team_frames.get(position.team_id)
            if panel:
                self._update_panel(panel, pokemon, owner, position)
        self._render_logs()

    def _owner_name(self, team_id: int) -> str:
        opponent = self.opponents.get(team_id)
        if opponent is None:
            return "Unknown"
        trainer = getattr(opponent, "trainer", None)
        if trainer:
            return trainer.name
        return "Wild"

    def refresh(self):
        battle_manager, opponent_1, opponent_2 = simulate_sample_battle()
        self.battle_manager = battle_manager
        self.opponents = {1: opponent_1, 2: opponent_2}
        self._render_state()

        # wire queue buttons to the freshly created battle
        for team_id, panel in self.team_frames.items():
            panel["queue_button"].configure(command=lambda tid=team_id: self.queue_move(tid))
            panel["burn_button"].configure(command=lambda tid=team_id: self.give_burn(tid))

    def queue_move(self, team_id: int):
        if self.battle_manager is None:
            return
        position = BattlePosition(team_id=team_id, pokemon_index=1)
        pokemon = self.battle_manager.position_manager.get_pokemon_at_position(position)
        if pokemon is None:
            # Print error instead of popup to surface in terminal
            print("Queue Move error: No pokemon at this position.")
            return

        move_name = self.team_frames[team_id]["move_var"].get()
        if not move_name:
            print("Queue Move error: Select a move first.")
            return

        try:
            # Resolve move index from the current Pokemon/BattleMon move set
            move_obj = pokemon.move_set.get_move_by_name(move_name)
            if move_obj is None:
                raise ValueError(f"Move '{move_name}' not found on this pokemon.")

            move_index = move_obj.index
            target_position = self.battle_manager.position_manager.get_direct_opponent_position(position)

            # Submit the move action directly to the battle manager
            self.battle_manager.submit_action(MoveAction(position=position, move_index=move_index, target_position=target_position))
        except Exception:
            # Print full traceback to terminal; let Tk keep running
            traceback.print_exc()
            return

        self._render_state()

    def end_turn(self):
        if self.battle_manager is None:
            return
        try:
            self.battle_manager.end_turn()
        except Exception:
            traceback.print_exc()
            return

        # Advance to the next turn if battle continues
        try:
            self.battle_manager.start_turn()
        except Exception:
            # if battle ended, ignore
            pass

        self._render_state()

    def give_burn(self, team_id: int):
        if self.battle_manager is None:
            return
        position = BattlePosition(team_id=team_id, pokemon_index=1)
        pokemon = self.battle_manager.position_manager.get_pokemon_at_position(position)
        if pokemon is None:
            print("Give Burn error: No pokemon at this position.")
            return

        burn = status_repository.get("freeze")
        if burn is None:
            print("Give Burn error: 'burn' status not found in repository.")
            return

        try:
            pokemon.status_conditions[burn] = 0  # 0 turns indicates persistent until cured
        except Exception:
            traceback.print_exc()
            return

        self._render_state()

    def run(self):
        self.root.mainloop()


def launch_battle_inspector():
    window = BattleInspectorWindow()
    window.run()


initialize_repositories(os.path.dirname(os.path.abspath(__file__)))



launch_battle_inspector()


# app = Application()
# app.run()