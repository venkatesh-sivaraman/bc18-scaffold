import battlecode as bc
import random
import sys
import traceback
from worker_logic import *

import os
print(os.getcwd())

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)

print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
#random.seed(6137)

# let's start off with some research!
# we can queue as much as we want.
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)

my_team = gc.team()

while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round())

    for unit in gc.my_units():

        if unit.unit_type == bc.UnitType.Worker:
            take_worker_action(gc, unit, my_team)
            continue
        try:
            # first, factory logic
            if unit.unit_type == bc.UnitType.Factory:
                garrison = unit.structure_garrison()
                if len(garrison) > 0:
                    d = random.choice(directions)
                    if gc.can_unload(unit.id, d):
                        print('unloaded a knight!')
                        gc.unload(unit.id, d)
                        continue
                elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
                    gc.produce_robot(unit.id, bc.UnitType.Knight)
                    print('HERE: produced a knight!')
                    continue

            # first, let's look for nearby blueprints to work on
            location = unit.location
            should_blueprint = True
            available_directions = set(directions)
            num_surround = 0
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    if unit.team == my_team:
                        num_surround += 1
                    if other.team != my_team:
                        should_blueprint = False
                        if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                            print('attacked a thing!')
                            gc.attack(unit.id, other.id)
                        elif other.location.is_on_map():
                            print('want to run away!')
                            relative_dir = location.map_location().direction_to(other.location.map_location())
                            available_directions.remove(relative_dir)


            # okay, there weren't any dudes around
            # pick a random direction:
            d = random.choice(list(available_directions))
            if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                gc.move_robot(unit.id, d)

        except Exception as e:
            print("Exception: {}".format(e))
            print(traceback.print_exc())


    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()
