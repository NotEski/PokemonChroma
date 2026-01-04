from engine.pokemon.repositry_generator import initialize_repositories
from engine.pokemon.repository import pokemon_repository, move_repository, item_repository, ability_repository, status_repository, hazard_repository
from engine.battle.battle_example import moveset_from_names, pickachu_eevee_battle_example
from engine.battle.battle_manager import BattleManager
from shared.battle.battle_header import BattleSwitchType, BattleType, BattleConfig
from shared.battle.position_manager import BattlePosition
from shared.battle.opponent import TrainerOpponent
from shared.trainer.trainer import Trainer
from shared.pokemon.pokemon import PokemonTeam, Pokemon
from shared.battle.battle_actions import MoveAction

import os
import traceback
import tkinter as tk
from tkinter import ttk


# Tkinter battle inspector helpers


def simulate_sample_battle():
    pikachu_moveset = moveset_from_names(["fissure", "trick_room", "volt_tackle", "quick_attack"])
    eevee_moveset = moveset_from_names(["tackle", "tail_whip", "bite", "quick_attack"])

    pikachu_base = pokemon_repository.get("pikachu")
    eevee_base = pokemon_repository.get("eevee")

    pikachu = Pokemon(pokemon_base=pikachu_base, level=50, move_set=pikachu_moveset)
    pikachu.nickname = "Pickle"
    pikachu.held_item = item_repository.get("light_ball")


    eevee = Pokemon(pokemon_base=eevee_base, level=50, move_set=eevee_moveset)
    eevee.nickname = "Stevie"
    eevee.held_item = item_repository.get("eviolite")


    marshtomp_moveset = moveset_from_names(["mud_slap", "water_gun", "rock_throw", "instakill"])
    marshtomp_base = pokemon_repository.get("marshtomp")
    marshtomp = Pokemon(pokemon_base=marshtomp_base, level=50, move_set=marshtomp_moveset)
    marshtomp.nickname = "Marshy"
    
    squirtle_moveset = moveset_from_names(["water_gun", "tackle", "bubble", "withdraw"])
    squirtle_base = pokemon_repository.get("squirtle")
    squirtle = Pokemon(pokemon_base=squirtle_base, level=50, move_set=squirtle_moveset)
    squirtle.nickname = "Squirt"

    youngseos_team = PokemonTeam(pokemons=[pikachu, eevee])
    trainer_1 = Trainer(name="Youngseo", team=youngseos_team)
    
    declans_team = PokemonTeam(pokemons=[marshtomp, squirtle])
    trainer_2 = Trainer(name="Declan", team=declans_team)

    opponent_1 = TrainerOpponent(trainer=trainer_1)
    opponent_2 = TrainerOpponent(trainer=trainer_2)

    battle_manager = BattleManager(teams=[opponent_1, opponent_2], battle_config=BattleConfig(battle_type=BattleType.SINGLE, is_wild=False, battle_switch_type=BattleSwitchType.SWITCH))
    battle_manager.init_battle()
    battle_manager.start_turn()

    return battle_manager, opponent_1, opponent_2


class BattleInspectorWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pokemon Chroma Battle Simulator")
        self.root.geometry("1500x1050")

        # Print full tracebacks to terminal for Tkinter callback errors
        def _tk_exception_printer(exc, val, tb):
            print("[Tkinter] Exception in callback:")
            traceback.print_exception(exc, val, tb)

        self.root.report_callback_exception = _tk_exception_printer

        self.turn_label = None
        self.battle_field_canvas = None
        self.team_panels = {}
        self.log_box = None
        self.opponents = {}
        self.battle_manager = None
        self.active_team_id = 1
        self.position_to_coords = {}

        self._build_layout()
        self.refresh()

    def _build_layout(self):
        header = ttk.Label(self.root, text="Battle Simulator", font=("Segoe UI", 16, "bold"))
        header.pack(pady=6)

        controls = ttk.Frame(self.root)
        controls.pack(fill="x", padx=10)
        ttk.Button(controls, text="Re-run Battle", command=self.refresh).pack(side="left")
        ttk.Button(controls, text="End Turn", command=self.end_turn).pack(side="left", padx=(8, 0))
        self.turn_label = ttk.Label(controls, text="Turn: 1")
        self.turn_label.pack(side="left", padx=12)

        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True, padx=10, pady=10)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=4)
        body.rowconfigure(1, weight=2)

        # Battle field on the left (larger)
        field_frame = ttk.LabelFrame(body, text="Battle Field (Top-Down View)")
        field_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 6))
        field_frame.columnconfigure(0, weight=1)
        field_frame.rowconfigure(0, weight=1)

        self.battle_field_canvas = tk.Canvas(field_frame, bg="#1c1c1c", highlightthickness=0, width=920, height=560)
        self.battle_field_canvas.grid(row=0, column=0, sticky="nsew")

        # Move controls for both teams under the field
        move_frame = ttk.Frame(body)
        move_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        move_frame.columnconfigure(0, weight=1)
        move_frame.rowconfigure(0, weight=1)
        move_frame.rowconfigure(1, weight=1)

        # Team 1 moves
        team1_move_frame = ttk.LabelFrame(move_frame, text="Team 1 Moves")
        team1_move_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 4))
        team1_move_frame.columnconfigure(0, weight=1)
        buttons_1 = ttk.Frame(team1_move_frame)
        buttons_1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        buttons_1.columnconfigure(0, weight=1)
        self.team_panels["move_buttons_frame_0"] = buttons_1
        ttk.Button(team1_move_frame, text="Switch", command=lambda: self.switch_selected_pokemon(0)).grid(row=0, column=1, padx=6, pady=5, sticky="n")

        # Team 2 moves
        team2_move_frame = ttk.LabelFrame(move_frame, text="Team 2 Moves")
        team2_move_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        team2_move_frame.columnconfigure(0, weight=1)
        buttons_2 = ttk.Frame(team2_move_frame)
        buttons_2.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        buttons_2.columnconfigure(0, weight=1)
        self.team_panels["move_buttons_frame_1"] = buttons_2
        ttk.Button(team2_move_frame, text="Switch", command=lambda: self.switch_selected_pokemon(1)).grid(row=0, column=1, padx=6, pady=5, sticky="n")

        # Right side panel with logs and team info
        right_panel = ttk.Frame(body)
        right_panel.grid(row=0, column=1, rowspan=2, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=2)
        right_panel.rowconfigure(1, weight=1)
        right_panel.rowconfigure(2, weight=1)

        # Log box
        log_frame = ttk.LabelFrame(right_panel, text="Battle Log")
        log_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.log_box = tk.Text(log_frame, height=18, state="disabled", wrap="word", font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=scrollbar.set)
        self.log_box.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Team rosters
        roster_frame_1 = ttk.LabelFrame(right_panel, text="Team 1 Roster")
        roster_frame_1.grid(row=1, column=0, sticky="nsew", pady=(0, 6))
        roster_frame_1.columnconfigure(0, weight=1)
        roster_frame_1.rowconfigure(0, weight=1)
        self.team_panels["roster_0"] = tk.Listbox(roster_frame_1, height=8, font=("Segoe UI", 10))
        self.team_panels["roster_0"].grid(row=0, column=0, sticky="nsew")
        r1_scroll = ttk.Scrollbar(roster_frame_1, orient="vertical", command=self.team_panels["roster_0"].yview)
        self.team_panels["roster_0"].configure(yscrollcommand=r1_scroll.set)
        r1_scroll.grid(row=0, column=1, sticky="ns")

        roster_frame_2 = ttk.LabelFrame(right_panel, text="Team 2 Roster")
        roster_frame_2.grid(row=2, column=0, sticky="nsew")
        roster_frame_2.columnconfigure(0, weight=1)
        roster_frame_2.rowconfigure(0, weight=1)
        self.team_panels["roster_1"] = tk.Listbox(roster_frame_2, height=8, font=("Segoe UI", 10))
        self.team_panels["roster_1"].grid(row=0, column=0, sticky="nsew")
        r2_scroll = ttk.Scrollbar(roster_frame_2, orient="vertical", command=self.team_panels["roster_1"].yview)
        self.team_panels["roster_1"].configure(yscrollcommand=r2_scroll.set)
        r2_scroll.grid(row=0, column=1, sticky="ns")

    def _draw_battle_field(self):
        """Draw the top-down battle field with pokemon and field effects."""
        if self.battle_field_canvas is None or self.battle_manager is None:
            return

        self.battle_field_canvas.delete("all")
        self.position_to_coords = {}

        canvas_width = int(self.battle_field_canvas.cget("width"))
        canvas_height = int(self.battle_field_canvas.cget("height"))

        # Define grid layout for battle field (2x3 grid)
        margin = 60
        cell_width = (canvas_width - 2 * margin) / 3
        cell_height = (canvas_height - 2 * margin) / 2

        # Draw grid
        for row in range(3):
            self.battle_field_canvas.create_line(
                margin, margin + row * cell_height,
                canvas_width - margin, margin + row * cell_height,
                fill="#555", width=2
            )
        for col in range(4):
            self.battle_field_canvas.create_line(
                margin + col * cell_width, margin,
                margin + col * cell_width, canvas_height - margin,
                fill="#555", width=2
            )

        # Draw all registered positions
        positions = self.battle_manager.position_manager.list_registered_positions()
        for position in positions:
            team_id = position.team_id
            pokemon_index = position.pokemon_index

            # Calculate position on grid (teams on opposite sides)
            if team_id == 0:
                col = pokemon_index
                row = 0
            else:
                col = pokemon_index
                row = 1

            cell_x = margin + col * cell_width
            cell_y = margin + row * cell_height

            center_x = cell_x + cell_width / 2
            center_y = cell_y + cell_height / 2

            self.position_to_coords[position] = (center_x, center_y)

            # Draw cell background
            self.battle_field_canvas.create_rectangle(
                cell_x, cell_y, cell_x + cell_width, cell_y + cell_height,
                fill="#0f0f0f", outline="#555", width=2
            )

            # Draw team label
            team_label = "Team 1" if team_id == 0 else "Team 2"
            self.battle_field_canvas.create_text(
                cell_x + 10, cell_y + 10,
                text=team_label,
                fill="#d0d0d0",
                font=("Segoe UI", 10, "bold"),
                anchor="nw"
            )

            # Get pokemon and field effects
            pokemon = self.battle_manager.position_manager.get_pokemon_at_position(position)
            field_effects = self.battle_manager.position_manager.field_effects.get(position, {})

            # Draw field effects
            if field_effects:
                effect_names = ", ".join([getattr(e, "name", str(e)) for e in field_effects.keys()])
                self.battle_field_canvas.create_text(
                    cell_x + 10, cell_y + 34,
                    text=f"Field: {effect_names}",
                    fill="#ffd54f",
                    font=("Segoe UI", 10),
                    anchor="nw",
                    width=int(cell_width - 28)
                )
            else:
                self.battle_field_canvas.create_text(
                    cell_x + 10, cell_y + 34,
                    text="Field: Clear",
                    fill="#999",
                    font=("Segoe UI", 10),
                    anchor="nw"
                )

            if pokemon:
                # Draw pokemon name and level
                base_name = getattr(pokemon.pokemon_base, "display_name", None) or getattr(pokemon.pokemon_base, "name", "-")
                self.battle_field_canvas.create_text(
                    center_x, center_y - 24,
                    text=f"{pokemon.nickname}",
                    fill="#ffffff",
                    font=("Segoe UI", 14, "bold"),
                    anchor="center"
                )
                self.battle_field_canvas.create_text(
                    center_x, center_y,
                    text=f"{base_name} | Lv {pokemon.level}",
                    fill="#e0e0e0",
                    font=("Segoe UI", 11),
                    anchor="center"
                )

                # Draw HP bar
                hp_ratio = max(0.0, min(1.0, pokemon.current_hp / pokemon.max_hp))
                bar_width = cell_width - 28
                bar_height = 14
                bar_x = center_x - bar_width / 2
                bar_y = center_y + 20

                # Background
                self.battle_field_canvas.create_rectangle(
                    bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
                    fill="#333", outline="#666", width=1
                )

                # HP fill
                hp_color = "#4caf50" if hp_ratio > 0.5 else ("#ffc107" if hp_ratio > 0.2 else "#f44336")
                self.battle_field_canvas.create_rectangle(
                    bar_x, bar_y, bar_x + bar_width * hp_ratio, bar_y + bar_height,
                    fill=hp_color, outline=hp_color, width=0
                )

                # HP text
                self.battle_field_canvas.create_text(
                    center_x, bar_y + bar_height / 2,
                    text=f"{pokemon.current_hp}/{pokemon.max_hp}",
                    fill="#ffffff",
                    font=("Segoe UI", 9, "bold"),
                    anchor="center"
                )

                # Status effects
                status_text = self._format_status(pokemon)
                if status_text != "none":
                    self.battle_field_canvas.create_text(
                        center_x, bar_y + bar_height + 14,
                        text=f"Status: {status_text}",
                        fill="#ff8fb1",
                        font=("Segoe UI", 10),
                        anchor="center"
                    )

                # Highlight active pokemon
                action = self.battle_manager.position_manager.get_position_action(position)
                if action:
                    self.battle_field_canvas.create_rectangle(
                        cell_x + 2, cell_y + 2, cell_x + cell_width - 2, cell_y + cell_height - 2,
                        outline="#ff9800", width=3
                    )
            else:
                self.battle_field_canvas.create_text(
                    center_x, center_y,
                    text="[Empty]",
                    fill="#777",
                    font=("Segoe UI", 11),
                    anchor="center"
                )

    def _render_team_roster(self, team_id: int):
        """Populate a team's roster listbox with all BattleMons."""
        roster = self.team_panels.get(f"roster_{team_id}")
        opponent = self.opponents.get(team_id)
        if not roster or self.battle_manager is None or opponent is None:
            return

        roster.delete(0, tk.END)

        battlemons = opponent.get_all_battlemons() if hasattr(opponent, "get_all_battlemons") else []
        for i, pokemon in enumerate(battlemons):
            base_name = getattr(pokemon.pokemon_base, "display_name", None) or getattr(pokemon.pokemon_base, "name", "-")
            hp_text = f"{pokemon.current_hp}/{pokemon.max_hp}"
            status = self._format_status(pokemon)
            status_text = f" [{status}]" if status != "none" else ""
            roster.insert(tk.END, f"{i}. {pokemon.nickname} ({base_name}) - Lv {pokemon.level} - HP: {hp_text}{status_text}")

    def _render_all_rosters(self):
        self._render_team_roster(0)
        self._render_team_roster(1)

    def _format_status(self, pokemon) -> str:
        """Get status condition names from a BattleMon."""
        if not hasattr(pokemon, "status_conditions"):
            return "none"
        
        statuses_dict = pokemon.status_conditions
        statuses = list(statuses_dict.keys()) if statuses_dict else []
        if not statuses:
            return "none"
        names = ", ".join([getattr(s, "name", str(s)) for s in statuses])
        return names

    def refresh(self):
        battle_manager, opponent_1, opponent_2 = simulate_sample_battle()
        self.battle_manager = battle_manager
        self.opponents = {0: opponent_1, 1: opponent_2}
        self.active_team_id = 0
        self._draw_battle_field()
        self._render_all_rosters()
        self._update_move_selector()
        self._render_logs()
        self._update_turn_label()

    def _update_move_selector(self):
        """Refresh move buttons for both teams."""
        if self.battle_manager is None:
            return
        self._update_move_buttons(0)
        self._update_move_buttons(1)

    def _update_move_buttons(self, team_id: int):
        position = BattlePosition(team_id=team_id, pokemon_index=0)
        pokemon = self.battle_manager.position_manager.get_pokemon_at_position(position)

        moves_container = self.team_panels.get(f"move_buttons_frame_{team_id}")
        if not moves_container or pokemon is None:
            if moves_container:
                for widget in moves_container.winfo_children():
                    widget.destroy()
            return

        # Clear existing buttons
        for widget in moves_container.winfo_children():
            widget.destroy()

        # Create a button for each move, aligned horizontally
        for move in pokemon.move_set.moves.values():
            button_text = f"{move.name}\nPP {move.current_pp}/{move.pp}"
            button = ttk.Button(
                moves_container,
                text=button_text,
                command=lambda m=move, tid=team_id: self.queue_move(tid, m.index)
            )
            button.pack(side="left", padx=3, pady=3, fill="x")

    def queue_move(self, team_id: int, move_index: int = None):
        if self.battle_manager is None:
            return
        position = BattlePosition(team_id=team_id, pokemon_index=0)
        pokemon = self.battle_manager.position_manager.get_pokemon_at_position(position)
        if pokemon is None:
            print("Queue Move error: No pokemon at this position.")
            return

        if move_index is None:
            print("Queue Move error: No move index provided.")
            return

        try:
            print (f"Queuing move index {move_index} for Team {team_id}'s {pokemon.nickname}")
            target_position = self.battle_manager.position_manager.get_direct_opponent_position(position)
            self.battle_manager.submit_action(MoveAction(position=position, move_index=move_index, target_position=target_position))
        except Exception:
            traceback.print_exc()
            return

        self._draw_battle_field()
        self._render_logs()
        self._render_all_rosters()
        self._update_move_selector()

    def switch_selected_pokemon(self, team_id: int):
        """Queue a switch for the selected roster entry for the given team."""
        if self.battle_manager is None:
            return

        roster = self.team_panels.get(f"roster_{team_id}")
        opponent = self.opponents.get(team_id)
        if roster is None or opponent is None:
            return

        selection = roster.curselection()
        if not selection:
            print("Switch error: Select a pokemon first.")
            return

        switch_index = selection[0]
        battlemons = opponent.get_all_battlemons() if hasattr(opponent, "get_all_battlemons") else []
        if switch_index >= len(battlemons):
            print("Switch error: Invalid selection index.")
            return

        position = BattlePosition(team_id=team_id, pokemon_index=0)

        try:
            self.battle_manager.switch_pokemon(position, switch_index)
        except Exception:
            traceback.print_exc()
            return

        self._draw_battle_field()
        self._render_logs()
        self._render_all_rosters()
        self._update_move_selector()

    def end_turn(self):
        if self.battle_manager is None:
            return
        try:
            self.battle_manager.end_turn()
        except Exception:
            traceback.print_exc()
            return

        try:
            self.battle_manager.start_turn()
        except Exception:
            pass

        self._draw_battle_field()
        self._render_logs()
        self._update_turn_label()
        self._render_all_rosters()
        self._update_move_selector()

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
            pokemon.status_conditions[burn] = 0
        except Exception:
            traceback.print_exc()
            return

        self._draw_battle_field()

    def _update_turn_label(self):
        """Update the turn counter label."""
        if self.battle_manager:
            self.turn_label.config(text=f"Turn: {self.battle_manager.battle_state.turn_number}")

    def _render_logs(self):
        """Render battle logs to the log box."""
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", tk.END)
        if self.battle_manager:
            for log in self.battle_manager.battle_log.logs:
                log_text = self._format_log_line(log)
                self.log_box.insert(tk.END, log_text + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.see(tk.END)

    def _format_log_line(self, log):
        """Format a log entry for display."""
        prefix = f"[{log.log_type.value}] " if hasattr(log, "log_type") else ""
        if getattr(log, "description", ""):
            return prefix + log.description
        turn_no = getattr(log, "turn_number", None)
        if turn_no is not None:
            return f"{prefix}Turn {turn_no} started"
        return prefix + "No description provided"

    def run(self):
        self.root.mainloop()


def launch_battle_inspector():
    window = BattleInspectorWindow()
    window.run()


initialize_repositories(os.path.dirname(os.path.abspath(__file__)))

# pickachu_eevee_battle_example()

launch_battle_inspector()


# app = Application()
# app.run()