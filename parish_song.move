move("perish_song"):

    on_use:
        for target in active_pokemon():
            target.add_volatile(
                name="perish_song",
                turns=3
            )

    volatile("perish_song"):

        on_turn_end:
            self.turns -= 1
            if self.turns == 0:
                self.faint()

        on_switch_out:
            self.remove()
