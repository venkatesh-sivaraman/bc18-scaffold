import battlecode as bc
import random
import sys
import traceback

directions = list(bc.Direction)
dangerous_units = set([
    bc.UnitType.Knight
])

WORKER_MOVE = "worker_move"
WORKER_REPLICATE = "worker_replicate"
WORKER_BUILD = "worker_build"
WORKER_BLUEPRINT = "worker_bp"
WORKER_HARVEST = "worker_harvest"
WORKER_REPAIR = "worker_repair"

def take_worker_action(gc, unit, my_team):
    # Determine the composition of the nearby surroundings.
    surroundings = {}
    need_escape = False
    available_directions = set(directions)
    num_units_my_team = 0
    num_units_their_team = 0
    num_factories = 0
    buildable_objects = {}
    if unit.location.is_on_map():
        map_loc = unit.location.map_location()
        for direction in directions:
            try:
                new_direction = map_loc.add(direction)
                karbonite = gc.karbonite_at(map_loc)
                if gc.has_unit_at_location(new_direction):
                    other = gc.sense_unit_at_location(new_direction)
                    if other.team != my_team and other.unit_type in dangerous_units:
                        need_escape = True
                    available_directions.remove(direction)
                    if other.team == my_team:
                        if other.unit_type == bc.UnitType.Factory:
                            num_factories += 1
                        num_units_my_team += 1
                    else:
                        num_units_their_team += 1
                    if gc.can_build(unit.id, other.id):
                        buildable_objects[direction] = other
                    surroundings[direction] = (other, other.team == my_team, karbonite)
                else:
                    surroundings[direction] = (None, True, karbonite)
            except Exception as e:
                print("Error: {}".format(e))

    if num_units_my_team >= 6:
        return
    # If there is a dangerous unit, move away
    elif need_escape and gc.is_move_ready(unit.id):
        if len(available_directions) > 0:
            d = random.choice(list(available_directions))
            if gc.can_move(unit.id, d):
                gc.move_robot(unit.id, d)
    else:
        # Take a weighted random choice of possible actions:
        # move, harvest, blueprint, build, or replicate.

        # Everybody got choices... Yup
        choices = []
        if len(available_directions) > 0 and any(gc.can_move(unit.id, d) for d in available_directions):
            choices += [WORKER_MOVE] * 4 * (4 ** num_factories)
        if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() / 2 and len(available_directions) > 1 and any(gc.can_replicate(unit.id, d) for d in available_directions):
            choices += [WORKER_REPLICATE] * (len(available_directions) - 1)
        for _ in range(len([1 for x in surroundings if surroundings[x][2] > 0])):
            choices += [WORKER_HARVEST] * 3
        if num_factories == 0 and gc.karbonite() > bc.UnitType.Factory.blueprint_cost():
            choices += [WORKER_BLUEPRINT] * (len(directions) - num_units_my_team) * 15
        if len(buildable_objects) > 0:
            choices = [WORKER_BUILD]

        if len(choices) == 0:
            return
        action = random.choice(choices)
        candidate_directions = available_directions
        try:
            if action == WORKER_REPLICATE:
                candidate_directions &= set([d for d in directions if gc.can_replicate(unit.id, d)])
            elif action == WORKER_HARVEST:
                candidate_directions &= set([d for d in directions if surroundings[d][2] > 0])
            elif action == WORKER_BLUEPRINT:
                candidate_directions &= set([d for d in directions if gc.can_blueprint(unit.id, bc.UnitType.Factory, d)])
            elif action == WORKER_BUILD:
                candidate_directions = set(buildable_objects.keys())
        except Exception as e:
            pass
            #print("Error determining directions: {}".format(e))

        if len(candidate_directions) == 0:
            candidate_directions = set([bc.Direction.Center])
            action == WORKER_MOVE
        d = random.choice(list(candidate_directions))
        try:
            if action == WORKER_MOVE:
                gc.move_robot(unit.id, d)
            elif action == WORKER_REPLICATE:
                gc.replicate(unit.id, d)
            elif action == WORKER_HARVEST:
                gc.harvest(unit.id, d)
            elif action == WORKER_BLUEPRINT:
                gc.blueprint(unit.id, bc.UnitType.Factory, d)
            elif action == WORKER_BUILD:
                if d in buildable_objects:
                    gc.build(unit.id, buildable_objects[d].id)
        except Exception as e:
            pass
            #print("Error carrying out directions: {}".format(e))
