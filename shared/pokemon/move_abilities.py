# the idea with this file is to allow for moves that have funky effects for the move to have a script that will be called when the move is used
# example for "Parish Song" which causes all pokemon on the field to faint in 4 moves unless they switch out
# example 2 "Metronome" which calls a random move from the entire move list
# These will be laoded into an effect engine that will have different hooks for different parts of the battle flow
# e.g. before move, after move, on switch in, on switch out, on faint, on status condition applied, etc.
# it will have a counter part system that will allow for abilities and items to have similar scripts that can be called at the same hooks
# The scripts will be stored in a way that they can be easily referenced by the move, ability, or item that uses them
# The scripts will only contain the functions that they override from the base move/ability/item behavior