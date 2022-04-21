import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# base_x: The corner of the map representing your base
base_x, base_y = [int(i) for i in input().split()]
heroes_per_player = int(input())  # Always 3


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


# game loop
while True:
    for i in range(2):
        # health: Your base health
        # mana: Ignore in the first league; Spend ten mana to cast a spell
        health, mana = [int(j) for j in input().split()]
    entity_count = int(input())  # Amount of heros and monsters you can see
    entities = []
    heroes = []
    for i in range(entity_count):
        # _id: Unique identifier
        # _type: 0=monster, 1=your hero, 2=opponent hero
        # x: Position of this entity
        # shield_life: Ignore for this league; Count down until shield spell fades
        # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
        # health: Remaining health of this monster
        # vx: Trajectory of this monster
        # near_base: 0=monster with no target yet, 1=monster targeting a base
        # threat_for: Given this monster's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
        (
            id,
            type,
            x,
            y,
            shield_life,
            is_controlled,
            health,
            vx,
            vy,
            near_base,
            threat_for,
        ) = [int(j) for j in input().split()]
        entity = {
            "id": id,
            "type": type,
            "x": x + vx,
            "y": y + vy,
            "shield_life": shield_life,
            "is_controlled": is_controlled,
            "health": health,
            "vx": vx,
            "vy": vy,
            "near_base": near_base,
            "threat_for": threat_for,
        }
        entities.append(entity)
        if type == 1:
            heroes.append(entity)
    dangers = [e for e in entities if e["type"] == 0 and e["threat_for"] == 1]
    dangers.sort(key=lambda e: distance(e["x"], e["y"], base_x, base_y))
    heroes_choices = []
    chosen = [0] * heroes_per_player
    orders = ["WAIT"] * heroes_per_player
    if dangers:
        # Enemies are sort by priority and distance for each hero
        for hero in heroes:
            d = dangers.copy()
            d.sort(
                key=lambda e: distance(e["x"], e["y"], hero["x"], hero["y"])
                - 10e5 * e["near_base"]
                + distance(e["x"], e["y"], base_x, base_y)
            )
            heroes_choices.append(d)

        def key(hero):
            closest = heroes_choices[hero["id"]][0]
            return distance(closest["x"], closest["y"], hero["x"], hero["y"])

        heroes.sort(key=key)

        # Every hero target a different target
        for i in range(heroes_per_player):
            hero = heroes[i]
            for choice in range(len(heroes_choices[i])):
                enemy = heroes_choices[i][choice]
                for j in range(i):
                    ally = heroes[j]
                    if i == j:
                        continue
                    dally = distance(enemy["x"], enemy["y"], ally["x"], ally["y"])
                    dme = distance(enemy["x"], enemy["y"], hero["x"], hero["y"])
                    # If an ally is already targeting the enemy, we don't target this enemy
                    if dally <= dme and heroes_choices[j].index(enemy) <= chosen[j]:
                        break
                else:
                    # If no ally is already targeting the enemy, we target it
                    orders[i] = "MOVE {} {}".format(enemy["x"], enemy["y"])
                    chosen[i] = choice
                    break
            else:
                # If no enemy is available, we target the closest to the base
                closest = dangers[0]
                orders[i] = "MOVE {} {}".format(closest["x"], closest["y"])
    
    print(chosen, [e["id"] for e in dangers], file=sys.stderr, flush=True)
    for i in range(heroes_per_player):
        print(orders[i])

        # To debug: print("Debug messages...", file=sys.stderr, flush=True)
        # In the first league: MOVE <x> <y> | WAIT; In later leagues: | SPELL <spellParams>;
