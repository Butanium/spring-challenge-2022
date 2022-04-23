import sys
from math import sqrt, cos, sin, pi
from traceback import format_exc
from random import random, seed

# Game statement for GitHub copilot
GAME_STATEMENT = """
# The Goal
Protect your base from spider attacks and outlive your opponent.


# Rules
Both players controls a team of 3 heroes. The teams start out at opposite corners of the map, near their base. Throughout the game spiders will appear regularly on the edges of the map. If a spider reaches your base, it will deal damage. If your base takes too much damage, you lose.
Thankfully, your heroes can kill spiders.


# The map
The game is played on a rectangular map where the coordinate X=0, Y=0 is the top-left pixel and X=17630, Y=9000 is the bottom-right pixel.
Fog makes it impossible to know the positions of all spiders and rival heroes. You need to have them within 2200 units from one of your heroes or 6000 from your base.
Each base can take a maximum of 3 points of damage before being destroyed.
Multiple entities (heroes & spiders) can occupy the same coordinates, there is no collision.


# Heroes
Every turn, you must provide a command for each hero. They may perform any of the following commands:
WAIT, the hero remains where they are.
MOVE, followed by map coordinates will make the hero advance towards that point by a maximum of 800 units.
SPELL, followed by a spell action, as detailed in the Spells section further below.
Heroes cannot be killed and cannot leave the map.
After a hero's move phase, any spiders within 800 units will suffer 2 points of damage.


# Spiders
Every spider appears with a given amount of health. If at the end of a turn, a spider's health has dropped to zero or below, the spider is removed from the game.
Spiders will appear randomly, but symmetrically from the map edges outside of the player's bases. They appear with a random moving direction.
Spiders will always advance in a straight line at a speed of 400 units per turn.
If a spider comes within 5000 units of a base at the end of a turn, it will target that base.
When targeting a base, a spider will move directly towards that base and can no longer leave the map.
If a spider is pushed (with a WIND command) outside the radius of a targeted base, it will stop targeting and start moving in a randomly selected direction.
If a spider comes within 300 units of a base at the end of a turn, as long as it has not been killed on this turn, it will disappear and deal the base 1 point of damage.
Each subsequent spider may have slightly more starting health than any previous spider.


# Spells
Your team will also acquire 1 point of mana per damage dealt to a spider, even from spiders with no health left.
Mana is shared across the team and heroes can spend 10 mana points to cast a spell.
A spell command has parameters, which you must separate with a space.

Spell table :
command	parameters	| effect | range
WIND	<x> <y>	| All entities (except your own heroes) within 1280 units are pushed 2200 units in the direction from the spellcaster to x,y. | 1280
SHIELD	<entityId> | The target entity cannot be targeted by spells for the next 12 rounds. | 2200
CONTROL	<entityId> <x> <y> | Override the target's next action with a step towards the given coordinates. | 2200
A hero may only cast a spell on entities that are within the spell's range from the hero.


# Victory Conditions
Your opponent's base health has dropped to zero.
You have more base health points than your opponent after 220 turns.
In case of a tie, you have gained the highest amount of wild mana: mana gained outside the radius of your base.
Defeat Conditions
Your base's health reaches zero.
Your program does not provide a valid command in time.


# Technical Details
After an entity moves towards a point, its coordinates are truncated (when below halfway across the map) or rounded up (when above halfway across the map), only then are distance-based calculations performed (such as spider damage).
Spells are cast in the order of the received output. This means a spell may be cancelled if another hero spent the necessary mana earlier in the turn.
If an entity is being moved via a CONTROL from multiple sources at once, it will move to the average of all computed destinations.
If an entity is being moved via a WIND from multiple sources at once, it will move to the sum of all given directions.
SHIELD also protects entities from receiving a new SHIELD.
Using a spell against a shielded entity still costs mana.
Players are not given the coordinates of spiders outside the map.
A spider can be pushed outside of the map, unless it is within a base radius, in which case it will will be moved no further than the border.
In case of a tie, the player who gained the highest amount of mana outside the radius of their base will win. this is called wild mana.


# Action order for one turn
Wait for both players to output 3 commands.
CONTROL spells are applied to the targets and will only be effective on the next turn, after the next batch of commands.
SHIELD spells are applied to the targets and will only be effective on the next turn, after the next batch of commands. Does not protect from a spell from this same turn.
MOVE all heroes.
Heroes attack spiders in range and produce mana for each hit.
WIND spells are applied to entities in range.
MOVE all spiders according to their current speed, unless they were pushed by a wind on this turn.
SHIELD countdowns are decremented.
New spiders appear. Dead spiders are removed.


# Game Input/Output
Initialization Input
Line 1: two integers baseX and baseY for the coordinates of your base. The enemy base will be at the opposite side of the map.
Line 2: the integer heroesPerPlayer which is always 3.

Input for One Game Turn
First 2 lines: two integers baseHealth and mana for the remaining health and mana for both players. Your data is always given first.
Next line: entityCount for the amount of game entities currently visible to you.
Next entityCount lines: 11 integers to describe each entity:
id: entity's unique id.
type:
0: a spider
1: one of your heroes
2: one of your opponent's heroes
x & y: the entity's position.
shieldLife: the number of rounds left until entity's shield is no longer active. 0 when no shield is active.
isControlled: 1 if this entity is under a CONTROL spell, 0 otherwise.
The next 5 integers only apply to spiders (will be -1 for heroes).
health: spider's remaining health points.
vx & vy: spider's current speed vector, they will add this to their position for their next movement.
nearBase: 1: if spider is targeting a base, 0 otherwise.
threatFor:
With the spider's current trajectory — if nearBase is 0:
0: it will never reach a base.
1: it will eventually reach your base.
2: it will eventually reach your opponent's base.
If nearBase is 1: 1 if this spider is targeting your base, 2 otherwise.

Output for One Game Turn
3 lines, one for each hero, containing one of the following actions:
WAIT: the hero does nothing.
MOVE followed by two integers (x,y): the hero moves 800 towards the given point.
SPELL followed by a spell command: the hero attempts to cast the given spell.
You may append text to a command to have it displayed in the viewer above your hero.

Examples:
MOVE 8000 4500
SPELL WIND 80 40 casting a wind spell!
SPELL SHIELD 1
WAIT nothing to do...
You must provide a valid command to all heroes each turn, even if they are being controlled by your opponent.
Constraints
Response time per turn ≤ 50ms
Response time for the first turn ≤ 1000ms
"""

# TODO :
#  - Add defensive spell usage :
#          * SHIELD for attacked heroes
#          * SHIELD for secured spiders
#  - Add offensive spell usage :
#          * CONTROL to neutralize enemy heroes
#          *? WIND and CONTROL to send spiders to enemy base
#          *? SHIELD to protect dangerous spiders

# Init seed for reproducibility
seed(0xDEADBEEF)

# Game Constants
HERO_DPS = 2
MONSTER_SPEED = 400
HERO_SPEED = 800
HERO_ATTACK_RANGE = 800
MAX_X = 17630
MAX_Y = 9000
BASE_VISION_RANGE = 6000
BASE_THRESHOLD_RANGE = 5000  # If a spider is within this range of a base, it will target it
HERO_VISION_RANGE = 2200
SPELL_RANGES = {'WIND': 1280, 'SHIELD': 2200, 'CONTROL': 2200}
MAX_SPELL_RANGE = 2200
SPELL_COSTS = {'WIND': 10, 'SHIELD': 10, 'CONTROL': 10}
WIND = 'WIND'
SHIELD = 'SHIELD'
CONTROL = 'CONTROL'

# Algorithm Constants
ROUND_ERROR = 1
RANDOM_SEARCH_RANGE = HERO_VISION_RANGE / 2
MAX_SPOT_RANGE = HERO_VISION_RANGE * 1.5
INFINITY = 10e10


# ------ Utility Functions ------ #


def debug(*args):
    print(*args, file=sys.stderr, flush=True)


def wrapper(func):
    # Reduce dictionaries with "x" and "y" keys and tuple/list to a single tuple before feeding it to func
    def result(*args):
        res = []
        for arg in args:
            if type(arg) == dict:
                res.append(arg['x'])
                res.append(arg['y'])
            elif type(arg) == int or type(arg) == float:
                res.append(arg)
            else:
                res.append(arg[0])
                res.append(arg[1])
        return func(*res)

    return result


# ~~ Vector functions ~~ #

@wrapper
def normalize_vector(x, y):
    length = sqrt(x ** 2 + y ** 2)
    return x / length, y / length


def rotate_vector(x, y, angle):
    return x * cos(angle) - y * sin(angle), x * sin(angle) + y * cos(angle)


@wrapper
def dist(x1, y1, x2, y2):
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


@wrapper
def direction(xs, ys, xe, ye):
    """ :arguments start, end"""
    return normalize_vector(xe - xs, ye - ys)


@wrapper
def end_point(x_start, y_start, x_end, y_end, distance):
    dx, dy = direction(x_start, y_start, x_end, y_end)
    return x_start + distance * dx, y_start + distance * dy


@wrapper
def closest_point_of_segment(xa, ya, xb, yb, xp, yp):
    u = [xa - xp, ya - yp]
    v = [xb - xa, yb - ya]
    vu = v[0] * u[0] + v[1] * u[1]
    vv = v[0] ** 2 + v[1] ** 2
    t = -vu / vv
    if 0 <= t <= 1:
        return xa + t * v[0], ya + t * v[1]
    else:
        return min((xa, ya), (xb, yb), key=lambda p: dist(xp, yp, p))


@wrapper
def round_vector(x, y):
    return round(x), round(y)


""" arguments : segment start, segment end, point """
# ------ End of Utility Functions ------ #


# --------- First turn input --------- #
base_x, base_y = [int(i) for i in input().split()]
base = {'x': base_x, 'y': base_y}
enemy_base = {'x': MAX_X - base_x, 'y': MAX_Y - base_y}
heroes_per_player = int(input())  # Always 3
_direction = 1 if enemy_base['x'] > base['x'] else -1


# ----- End of first turn input ------ #


# --------- Game Functions --------- #
@wrapper
def move_to(x, y):
    return "MOVE {} {}".format(round(x), round(y))


def closest_target_point(hero, primary_target, secondary_target):
    end_segment = end_point(secondary_target, primary_target, HERO_ATTACK_RANGE - ROUND_ERROR)
    start_segment = end_point(primary_target, secondary_target, HERO_ATTACK_RANGE - ROUND_ERROR)
    return round_vector(closest_point_of_segment(start_segment, end_segment, hero))


def is_fatal(spider):
    t = dist(spider, base) / MONSTER_SPEED
    return spider['health'] - t * HERO_DPS > 0


@wrapper
def control_entity(_id, end_x, end_y):
    """ arguments : spider id, direction x, direction y """
    return "SPELL CONTROL {} {} {}".format(_id, round(end_x), round(end_y))


@wrapper
def wind(end_x, end_y):
    return "SPELL WIND {} {}".format(round(end_x), round(end_y))


def defense_control(spider):
    dx, dy = direction(base, spider)
    return control_entity(spider['id'], spider['x'] + dx * 10e5, spider['y'] + dy * 10e5)


def defense_wind(spider, hero):
    dx, dy = direction(base, spider)
    return wind(hero["x"] + dx * 10e5, hero['y'] + dy * 10e5)


def attack_spider(hero, spider, danger, wildlife, mana):
    spider_dist = dist(spider, hero)
    if is_fatal(spider):
        debug("%d : shit ! %d" % (hero['id'], spider['id']))
    if is_fatal(spider) and not spider['shield_life'] and spider_dist <= MAX_SPELL_RANGE and mana >= 10:
        dist_to_base = dist(spider, base)
        if dist_to_base > BASE_THRESHOLD_RANGE - 400 + ROUND_ERROR:
            # If spider is close to the edge make it move to the enemy base
            return defense_control(spider)
        if spider_dist > SPELL_RANGES[WIND] - ROUND_ERROR and dist_to_base / MONSTER_SPEED <= 2:
            # Control if the spider is very close to the base and too far to use wind
            return defense_control(spider)
        elif spider_dist <= SPELL_RANGES[WIND] - ROUND_ERROR:
            # Use wind if the spider is close enough
            return defense_wind(spider, hero)

    if spider_dist > HERO_SPEED:
        return move_to(spider)
    # Tries to find a secondary target to attack at the same time as the spider
    filtre = lambda s: dist(s, spider) <= 2 * HERO_ATTACK_RANGE - 2 * ROUND_ERROR and spider['id'] != s['id']

    targets = filter(filtre, danger)
    for target in targets:
        target_point = closest_target_point(hero, spider, target)
        if dist(target_point, hero) + ROUND_ERROR <= HERO_SPEED:
            debug("{} optimize {} by adding {}dist_to_spider :{}, dist_to_other: {}\n".format(debug_small(hero),
                                                                                              debug_small(spider),
                                                                                              debug_small(target),
                                                                                              round(dist(target_point,
                                                                                                         spider), 2),
                                                                                              round(dist(target_point,
                                                                                                         target), 2)))
            return move_to(target_point) + " opt"
    wild_targets = filter(filtre, wildlife)
    for target in wild_targets:
        target_point = closest_target_point(hero, spider, target)
        if dist(target_point, hero) <= HERO_SPEED:
            debug("{} optimize {} by adding {}dist_to_spider :{}, dist_to_other: {}\n".format(debug_small(hero),
                                                                                              debug_small(spider),
                                                                                              debug_small(target),
                                                                                              round(dist(target_point,
                                                                                                         spider), 2),
                                                                                              round(dist(target_point,
                                                                                                         target), 2)))
            return move_to(target_point) + " opt"
    # If no secondary target is found, move to the spider
    return move_to(spider)


def get_spot_direction(_id):
    theta = ((_id + 1) % 3) * pi / 5
    direction = 1 if enemy_base['x'] > base['x'] else -1
    return normalize_vector(rotate_vector(direction, 0, theta))


def get_spot(_id):
    # Observation spot foreach hero
    dirx, diry = get_spot_direction(_id)
    return base_x + dirx * BASE_VISION_RANGE, base_y + diry * BASE_VISION_RANGE


def scout(hero, spiders):
    # Default hero behavior
    first_x, first_y = get_spot(hero['id'])
    if spiders:
        closest = min(spiders,
                      key=lambda e: dist(e, hero))
        if dist(first_x, first_y, closest) <= MAX_SPOT_RANGE:
            # If no threat get the wild mana by killing neutral spiders
            return move_to(closest) + " farm"

    # Else move randomly around the observation post
    random_theta = random() * pi - pi / 2
    dirx, diry = get_spot_direction(hero['id'])
    random_dx, random_dy = rotate_vector(dirx, diry, random_theta)
    final_x = first_x + random_dx * RANDOM_SEARCH_RANGE
    final_y = first_y + random_dy * RANDOM_SEARCH_RANGE
    return move_to(final_x, final_y) + " scout"


def debug_small(entity):
    return "id : {} x : {} y : {}\n".format(entity['id'], entity['x'], entity['y'])


# ----- Game Functions End ------ #


# --------- Main Loop --------- #
turn = 0
while True:
    turn += 1
    # health: Your base health
    # mana: Spend ten mana to cast a spell
    my_health, my_mana = [int(j) for j in input().split()]
    opponent_health, opponent_mana = [int(j) for j in input().split()]
    entity_count = int(input())  # Amount of heroes and spiders you can see
    entities = []
    heroes = []
    # Spiders aiming toward our base
    dangers = []
    # Neutral spiders
    wildlife = []
    for i in range(entity_count):
        # _id: Unique identifier
        # _type: 0=spider, 1=your hero, 2=opponent hero
        # x: Position of this entity
        # shield_life: Count down until shield spell fades
        # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
        # health: Remaining health of this spider
        # vx: Trajectory of this spider
        # near_base: 0=spider with no target yet, 1=spider targeting a base
        # threat_for: Given this spider's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
        (_id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for) = \
            [int(j) for j in input().split()]
        entity = {"type": _type, "is_controlled": is_controlled, "health": health, "id": _id, "x": x, "y": y,
                  "near_base": near_base, "threat_for": threat_for, "vx": vx, "vy": vy, "shield_life": shield_life}
        entities.append(entity)
        if _type == 1:
            heroes.append(entity)
        if _type == 0:
            if threat_for == 1:
                dangers.append(entity)
            if not threat_for:
                wildlife.append(entity)
    non_ally_spiders = dangers + wildlife
    # The closer an entity is the higher danger it is
    # TODO? : more complex threat evaluation (use health maybe)
    dangers.sort(key=lambda e: dist(e, base))
    heroes_choices = []
    chosen = [10e10] * heroes_per_player
    orders = [scout(h, non_ally_spiders) for h in heroes]
    # debug([debug_small(h) for h in heroes])
    # - debug("scout orders : {}".format(orders))
    if dangers:
        # Enemies are sort by priority and distance for each hero
        for hero in heroes:
            d = dangers.copy()
            d.sort(
                key=lambda enemy: dist(enemy, hero) - 10e10 * enemy["near_base"] + dist(enemy, base)
            )
            heroes_choices.append(d)

        # Sort hero by distance to their closest target so that no hero targets a spider that is closer to another
        # inactive hero
        heroes.sort(key=lambda h: dist(heroes_choices[h["id"] % 3][0], h))

        # The heroes try to target different spiders
        for i in range(heroes_per_player):
            hero = heroes[i]
            hero_id = hero["id"] % 3
            for choice in range(len(heroes_choices[hero_id])):
                spider = heroes_choices[hero_id][choice]
                if spider['shield_life'] and (my_mana >= 20 or turn <= 40):
                    orders[hero_id] = attack_spider(hero, spider, dangers, wildlife, my_mana) + " P def %d" % spider[
                        'id']
                for j in range(i):
                    # If the spider has a shield or if we have low mana, the hero will target it : we skip this loop
                    ally = heroes[j]
                    d_ally = dist(spider, ally)
                    d_me = dist(spider, hero)
                    # If an ally is already targeting the spider, we don't target this spider
                    if d_ally <= d_me and heroes_choices[j].index(spider) <= chosen[j]:
                        break
                else:
                    # If no ally is already targeting the spider, we target it
                    orders[hero_id] = attack_spider(hero, spider, dangers, wildlife, my_mana) + " T def %d" % spider[
                        'id']
                    chosen[hero_id] = choice
                    break

    debug(*[debug_small(h) for h in heroes])
    for i in range(heroes_per_player):
        print("{} {}".format(orders[i % heroes_per_player], "[%d]" % (i % 3)))
