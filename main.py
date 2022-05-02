import sys
from math import sqrt, cos, sin, pi, ceil, floor
from random import random, seed

# Game statement for GitHub copilot
GAME_STATEMENT = """
# The Goal
Protect your base from spider attacks and outlive your opponent.


# Rules Both players controls a team of 3 heroes. The teams start out at opposite corners of the map, near their 
base. Throughout the game spiders will appear regularly on the edges of the map. If a spider reaches your base, 
it will deal damage. If your base takes too much damage, you lose. Thankfully, your heroes can kill spiders. 


# The map The game is played on a rectangular map where the coordinate X=0, Y=0 is the top-left pixel and X=17630, 
Y=9000 is the bottom-right pixel. Fog makes it impossible to know the positions of all spiders and rival heroes. You 
need to have them within 2200 units from one of your heroes or 6000 from your base. Each base can take a maximum of 3 
points of damage before being destroyed. Multiple entities (heroes & spiders) can occupy the same coordinates, 
there is no collision. 


# Heroes
Every turn, you must provide a command for each hero. They may perform any of the following commands:
WAIT, the hero remains where they are.
MOVE, followed by map coordinates will make the hero advance towards that point by a maximum of 800 units.
SPELL, followed by a spell action, as detailed in the Spells section further below.
Heroes cannot be killed and cannot leave the map.
After a hero's move phase, any spiders within 800 units will suffer 2 points of damage.


# Spiders Every spider appears with a given amount of health. If at the end of a turn, a spider's health has dropped 
to zero or below, the spider is removed from the game. Spiders will appear randomly, but symmetrically from the map 
edges outside of the player's bases. They appear with a random moving direction. Spiders will always advance in a 
straight line at a speed of 400 units per turn. If a spider comes within 5000 units of a base at the end of a turn, 
it will target that base. When targeting a base, a spider will move directly towards that base and can no longer 
leave the map. If a spider is pushed (with a WIND command) outside the radius of a targeted base, it will stop 
targeting and start moving in a randomly selected direction. If a spider comes within 300 units of a base at the end 
of a turn, as long as it has not been killed on this turn, it will disappear and deal the base 1 point of damage. 
Each subsequent spider may have slightly more starting health than any previous spider. 


# Spells
Your team will also acquire 1 point of mana per damage dealt to a spider, even from spiders with no health left.
Mana is shared across the team and heroes can spend 10 mana points to cast a spell.
A spell command has parameters, which you must separate with a space.

Spell table : command	parameters	| effect | range 
WIND	<x> <y>	| All entities (except your own heroes) within 1280 units are pushed 2200 units in the direction from 
the spell caster to x,y. | 1280 
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


# Technical Details After an entity moves towards a point, its coordinates are truncated (when below halfway across 
the map) or rounded up (when above halfway across the map), only then are distance-based calculations performed (such 
as spider damage). Spells are cast in the order of the received output. This means a spell may be cancelled if 
another hero spent the necessary mana earlier in the turn. If an entity is being moved via a CONTROL from multiple 
sources at once, it will move to the average of all computed destinations. If an entity is being moved via a WIND 
from multiple sources at once, it will move to the sum of all given directions. SHIELD also protects entities from 
receiving a new SHIELD. Using a spell against a shielded entity still costs mana. Players are not given the 
coordinates of spiders outside the map. A spider can be pushed outside of the map, unless it is within a base radius, 
in which case it will will be moved no further than the border. In case of a tie, the player who gained the highest 
amount of mana outside the radius of their base will win. this is called wild mana. 


# Action order for one turn Wait for both players to output 3 commands. CONTROL spells are applied to the targets and 
will only be effective on the next turn, after the next batch of commands. SHIELD spells are applied to the targets 
and will only be effective on the next turn, after the next batch of commands. Does not protect from a spell from 
this same turn. MOVE all heroes. Heroes attack spiders in range and produce mana for each hit. WIND spells are 
applied to entities in range. MOVE all spiders according to their current speed, unless they were pushed by a wind on 
this turn. SHIELD countdowns are decremented. New spiders appear. Dead spiders are removed. 


# Game Input/Output Initialization Input Line 1: two integers baseX and baseY for the coordinates of your base. The 
enemy base will be at the opposite side of the map. Line 2: the integer heroesPerPlayer which is always 3. 

Input for One Game Turn First 2 lines: two integers baseHealth and mana for the remaining health and mana for both 
players. Your data is always given first. Next line: entityCount for the amount of game entities currently visible to 
you. Next entityCount lines: 11 integers to describe each entity: id: entity's unique id. type: 0: a spider 1: one of 
your heroes 2: one of your opponent's heroes x & y: the entity's position. shieldLife: the number of rounds left 
until entity's shield is no longer active. 0 when no shield is active. isControlled: 1 if this entity is under a 
CONTROL spell, 0 otherwise. The next 5 integers only apply to spiders (will be -1 for heroes). health: spider's 
remaining health points. vx & vy: spider's current speed vector, they will add this to their position for their next 
movement. nearBase: 1: if spider is targeting a base, 0 otherwise. threatFor: With the spider's current trajectory — 
if nearBase is 0: 0: it will never reach a base. 1: it will eventually reach your base. 2: it will eventually reach 
your opponent's base. If nearBase is 1: 1 if this spider is targeting your base, 2 otherwise. 

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
#  - Don't track 2 times close enemies
#  - Allow critical defense for tracker
#  - Update enemy position when they get winded
#  - Add defensive spell usage :
#          * SHIELD for attacked heroes
#          *? SHIELD for secured spiders
#  - Add offensive spell usage :
#          * CONTROL to neutralize enemy heroes
#          *? WIND and CONTROL to send spiders to enemy base
#          *? SHIELD to protect dangerous spiders

# Init seed for reproducibility
seed(0xDEADBEEF)

# Game Constants
HERO_DPS = 2
SPIDER_SPEED = 400
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
WIND_DISTANCE = 2200
WIND = 'WIND'
SHIELD = 'SHIELD'
CONTROL = 'CONTROL'
# threat_for constants
ALLY = 1
ENEMY = 2
NEUTRAL = 0


# Entity class 
class Entity:
    def __init__(self, _id=-1, _type=None, is_controlled=None, health=None, x=None, y=None, near_base=None,
                 threat_for=None, vx=None, vy=None, shield_life=None, attackers=None, id3=None):
        self.id = _id
        self.type = _type
        self.is_controlled = is_controlled
        self.health = health
        self.x = x
        self.y = y
        self.near_base = near_base
        self.threat_for = threat_for
        self.vx = vx
        self.vy = vy
        self.shield_life = shield_life
        self.attackers = attackers
        self.id3 = id3

    def __hash__(self):
        return hash(self.id)


# --------- First turn input --------- #
base_x, base_y = [int(i) for i in input().split()]
base = Entity(x=base_x, y=base_y)
enemy_base = Entity(x=MAX_X - base_x, y=MAX_Y - base_y)
heroes_per_player = int(input())  # Always 3

# Algorithm Constants and global variables
INFINITY = 10e10
ROUND_ERROR = 1
SCOUT = 0
MIN_COMFY_MANA = 200
DEFENDER = 1
TRACKER = 2
PATROL_RANGE = BASE_VISION_RANGE + HERO_VISION_RANGE
RANDOM_SEARCH_RANGE = [2.5 * HERO_VISION_RANGE, HERO_VISION_RANGE, HERO_VISION_RANGE / 2]
MAX_SPOT_RANGE = [BASE_THRESHOLD_RANGE + 4 * HERO_VISION_RANGE, BASE_THRESHOLD_RANGE + 2 * HERO_VISION_RANGE,
                  HERO_VISION_RANGE - 2 * HERO_SPEED]
MAX_DEFENDER_DISTANCE = BASE_THRESHOLD_RANGE + 2 * HERO_VISION_RANGE
# If you are closer than this distance to a monster, farm it even if he is already attacked
MAX_FARM_DIST = 2 * HERO_SPEED
WIND_ONLY_NEAR_BASE = True
WIND_THRESHOLD = BASE_VISION_RANGE + HERO_VISION_RANGE
TRACK_THRESHOLD = BASE_THRESHOLD_RANGE + 1.5 * HERO_VISION_RANGE
TRACKER_RANGE = HERO_VISION_RANGE
ATTACKER_THRESHOLD = HERO_VISION_RANGE + HERO_SPEED
MAX_DIST_TO_ATTACKER = SPELL_RANGES[WIND] + HERO_SPEED + SPIDER_SPEED
# If one of our hero is closer than this distance to an entity that is supposed to be here and that is not seen,
# we delete it
MAX_DOUBT_DIST = HERO_VISION_RANGE * 0.75
# If we have more than this amount of mana, our hero will control attacker if he needs to get closer to him
MIN_MANA_FOR_CONTROL_TRACKING = 50
# If a spider is within this range of a base, even trackers will accept to target it if there are no allies near it
CRITICAL_RANGE = WIND_DISTANCE + 2 * SPIDER_SPEED

# -------- Global variables -------- #
report = ""
turn = 0
mana = 0
current_objective = [[]] * heroes_per_player
tracking: dict[Entity: Entity] = {}
defenders_id = []
min_comfy_mana = 200


# Key : tracker ally, value : tracked enemy


# ------ Utility Functions ------ #


def debug(*args):
    print(*args, file=sys.stderr, flush=True)


def wrapper_id(func):
    # Wrapper to allow function to take either an id or an Entity as argument
    def wrap(id_or_entity, *args, **kwargs):
        if isinstance(id_or_entity, Entity):
            _id = id_or_entity.id
        else:
            _id = id_or_entity
        return func(_id, *args, **kwargs)

    return wrap


def wrapper(func):
    # Reduce dictionaries with "x" and "y" keys and tuple/list and Entities to a single tuple before feeding it to func
    def result(*args, **kwargs):
        res = []
        for arg in args:
            if type(arg) == dict:
                res.append(arg['x'])
                res.append(arg['y'])
            elif type(arg) == int or type(arg) == float:
                res.append(arg)
            elif isinstance(arg, Entity):
                res.append(arg.x)
                res.append(arg.y)
            else:
                res.append(arg[0])
                res.append(arg[1])
        return func(*res, **kwargs)

    return result


def to_tuple(arg):
    if type(arg) == dict:
        return arg['x'], arg['y']
    elif isinstance(arg, Entity):
        return arg.x, arg.y
    else:
        return arg[0], arg[1]


# ~~ Vector functions ~~ #

@wrapper
def normalize_vector(x, y):
    length = sqrt(x ** 2 + y ** 2)
    return x / length, y / length


@wrapper
def rotate_vector(x, y, angle):
    return x * cos(angle) - y * sin(angle), x * sin(angle) + y * cos(angle)


@wrapper
def dist(x1, y1, x2, y2):
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


@wrapper
def get_direction(xs, ys, xe, ye):
    """ :arguments start, end"""
    return normalize_vector(xe - xs, ye - ys)


@wrapper
def end_point(x_start, y_start, x_end, y_end, distance):
    dx, dy = get_direction(x_start, y_start, x_end, y_end)
    return x_start + distance * dx, y_start + distance * dy


@wrapper
def closest_point_of_segment(xa, ya, xb, yb, xp, yp, is_line_before=False, is_line_after=False):
    """ arguments : segment start, segment end, point """
    u = [xa - xp, ya - yp]
    v = [xb - xa, yb - ya]
    vu = v[0] * u[0] + v[1] * u[1]
    vv = v[0] ** 2 + v[1] ** 2
    t = -vu / vv
    if (0 <= t or is_line_before) and (t <= 1 or is_line_after):
        return xa + t * v[0], ya + t * v[1]
    else:
        return min((xa, ya), (xb, yb), key=lambda p: dist(xp, yp, p))


@wrapper
def round_vector(x, y):
    return round(x), round(y)


@wrapper
def scale_vector(x, y, scale):
    return x * scale, y * scale


# ------ End of Utility Functions ------ #


# --------- Game Functions --------- #


@wrapper
def clamp_to_map(x, y):
    return max(0, min(x, MAX_X)), max(0, min(y, MAX_Y))


@wrapper
def move_to(x, y):
    return "MOVE {} {}".format(round(x), round(y))


def partial_move_to(hero, target, distance):
    direction = get_direction(hero, target)
    dx, dy = scale_vector(direction, distance)
    return move_to(hero.x + dx, hero.y + dy) + " 2far"


def closest_target_point(hero, primary_target, secondary_target):
    end_segment = end_point(secondary_target, primary_target, HERO_ATTACK_RANGE - ROUND_ERROR)
    start_segment = end_point(primary_target, secondary_target, HERO_ATTACK_RANGE - ROUND_ERROR)
    return round_vector(closest_point_of_segment(start_segment, end_segment, hero))


@wrapper_id
def is_tracked(_id):
    return _id in [t.id for t in tracking.values()]


@wrapper_id
def is_tracking(_id):
    return _id in [h.id for h in tracking.keys()]


def should_be_seen(entity, heroes):
    for hero in heroes:
        if dist(hero, entity) <= MAX_DOUBT_DIST:
            return True
    return False


def clean_tracking(heroes, enemies):
    enemies_ids = [e.id for e in enemies]
    to_remove = []
    for key, attacker in tracking.items():
        if attacker.id not in enemies_ids and should_be_seen(attacker, heroes):
            to_remove.append(key)
    for key in to_remove:
        del tracking[key]


def update_tracking(heroes):
    to_delete = []
    to_add = []
    for hero in heroes:
        for tracker, target in tracking.items():
            if hero.id == tracker.id and hero != tracker:
                to_add.append((hero, target))
                to_delete.append(tracker)
    for tracker in to_delete:
        del tracking[tracker]
    for tracker, target in to_add:
        tracking[tracker] = target


def retrack(attacker, heroes):
    res = None
    for tracker, target in tracking.items():
        if attacker.id == target.id:
            res = tracker
            break
    del tracking[res]
    new_key = next((h for h in heroes if h.id == res.id))
    tracking[new_key] = attacker


def track(attacker, heroes):
    tracker = min((h for h in heroes if not is_tracking(h)), key=lambda h: dist(h, attacker))
    tracking[tracker] = attacker


@wrapper_id
def untrack(_id):
    to_delete = []
    for tracker, target in tracking.items():
        if target.id == _id:
            to_delete.append(tracker)
    for tracker in to_delete:
        del tracking[tracker]


def get_tracked_target(_id):
    for tracker, target in tracking.items():
        if _id == tracker.id:
            return target


def time_left(distance, speed):
    return ceil(int(distance) / speed)


def time_to(spider, to=None, speed=SPIDER_SPEED):
    if to is None:
        to = base
    return floor(floor(dist(spider, to)) / speed)


def is_fatal(spider):
    # debug(f"{spider.id} {time_to(spider)}")
    t = time_to(spider)
    return spider.health - t * HERO_DPS >= 0


def is_critical(spider):
    return is_attacking_base(spider) and (dist(base, spider) <= CRITICAL_RANGE or bool(spider.shield_life))


def dist_to_closest_attacker(spider, ammo_spiders):
    if spider not in ammo_spiders.keys():
        return INFINITY
    return min(dist(spider, e) for e in ammo_spiders[spider])


def target_cost_key(hero, ammo_spiders: dict):
    def key(spider):
        threat = spider.threat_for
        near_my_base = threat == 1 and spider.near_base
        time_to_base = time_to(spider)
        if spider in ammo_spiders.keys():
            attackers = ammo_spiders[spider]
            d_min = min(dist(spider, a) for a in attackers)
            return [-is_critical(spider) if threat == ALLY else 0,
                    d_min > ATTACKER_THRESHOLD,
                    time_to_base if near_my_base else INFINITY,
                    d_min,
                    int(dist(spider, hero))
                    ]
        return [-is_critical(spider) if threat == ALLY else (1 if threat == NEUTRAL else 2),
                2 if threat == ENEMY else 1 - spider.near_base,
                time_to_base if near_my_base else INFINITY,
                INFINITY,  # cannot be used as an ammo
                int(dist(spider, hero))]

    return key


@wrapper_id
@wrapper
def control_entity(_id, end_x, end_y):
    """ arguments : spider id, direction x, direction y """
    return "SPELL CONTROL {} {} {}".format(_id, round(end_x), round(end_y))


@wrapper
def wind(end_x, end_y):
    return "SPELL WIND {} {}".format(round(end_x), round(end_y))


def defense_control(spider):
    global mana
    mana -= SPELL_COSTS[CONTROL]
    dx, dy = get_direction(base, spider)
    return control_entity(spider.id, spider.x + dx * 10e5, spider.y + dy * 10e5)


def defense_wind(spider, hero):
    global mana
    mana -= SPELL_COSTS[WIND]
    dx, dy = get_direction(base, spider)
    return wind(hero.x + dx * 10e5, hero.y + dy * 10e5)


def attack_spider(hero, spider, other_spiders, ammo_spiders):
    global mana
    current_objective[hero.id3] = []
    spider_dist = dist(spider, hero)
    dist_to_base = dist(spider, base)
    if is_fatal(spider):
        debug("%d : shit ! %d" % (hero.id, spider.id))
    # if we have enough mana get more wild mana

    if ((mana > min_comfy_mana or dist_to_closest_attacker(spider, ammo_spiders) <= MAX_DIST_TO_ATTACKER)
        and (dist_to_base < WIND_THRESHOLD or not WIND_ONLY_NEAR_BASE) or is_fatal(spider)) \
            and not spider.shield_life and dist_to_base > ceil(BASE_THRESHOLD_RANGE - WIND_DISTANCE) and \
            spider_dist + ROUND_ERROR <= SPELL_RANGES[WIND] and mana >= SPELL_COSTS[WIND]:
        return defense_wind(spider, hero) + (" wcomfy" if mana > min_comfy_mana else " wtrack")
    if (dist_to_closest_attacker(spider, ammo_spiders) <= SPELL_RANGES[WIND] or is_fatal(
            spider)) and not spider.shield_life and ceil(spider_dist) <= MAX_SPELL_RANGE and mana >= \
            SPELL_COSTS[WIND]:
        if ceil(spider_dist) <= SPELL_RANGES[WIND]:
            # Use wind if the spider is close enough
            return defense_wind(spider, hero) + " wclose"
        # elif spider_dist > SPELL_RANGES[WIND] - ROUND_ERROR + HERO_SPEED and time_to(spider) == 2:
        #     # Control if the spider is very close to the base and too far to use wind
        #     return defense_control(spider)

    if spider_dist > HERO_SPEED:
        spot = get_spot(hero.id)
        role = get_role(hero)
        # if the spider is too far away from the spot and that the hero is close to the spot, stay closer to the spot
        if dist(spider, spot) > MAX_SPOT_RANGE[role] >= dist(hero, spot) and not is_critical(spider):
            # debug(f"spot: {spot} role: {role} id: {hero.id}")
            partial_move_to(hero, spider, MAX_SPOT_RANGE[role] - dist(hero, spot))
        else:
            return move_to(spider)
    # Tries to find a secondary target to attack at the same time as the spider
    filtre = lambda s: ceil(dist(s, spider)) <= 2 * HERO_ATTACK_RANGE and spider.id != s.id

    targets = list(filter(filtre, other_spiders))
    targets.sort(key=target_cost_key(hero, ammo_spiders))
    for target in targets:
        if is_fatal(target) and ceil(dist(target, hero)) <= SPELL_RANGES[WIND] and mana >= SPELL_COSTS[WIND] and not \
                target.shield_life:
            return defense_wind(target, hero) + " optwind"
        target_point = closest_target_point(hero, spider, target)
        if dist(target_point, hero) + ROUND_ERROR <= HERO_SPEED:
            return move_to(target_point) + " opt"
    # If no secondary target is found, just move normally to the spider
    # todo? optimize move to
    return move_to(spider)


def get_spot_direction(_id):
    theta = ((_id + 1) % 3) * pi / 5
    direction = 1 if enemy_base.x > base.x else -1
    return normalize_vector(rotate_vector(direction, 0, theta))


def get_spot(_id, ignore_role=False):
    # Observation spot foreach hero
    if is_tracking(_id) and not ignore_role:
        return get_tracked_target(_id)
    if not ignore_role:
        return base.x, base.y
    dir_x, dir_y = get_spot_direction(_id % 3)
    return base_x + dir_x * BASE_VISION_RANGE, base_y + dir_y * BASE_VISION_RANGE


spots = [get_spot(i, ignore_role=True) for i in range(3)]


def is_valid_spot(spot, hero, allies):
    d_me = dist(spot, hero)
    for ally in allies:
        objective = current_objective[ally.id3]
        if objective and ally.id != hero.id and int(dist(spot, ally)) <= int(d_me) and \
                dist(objective[0], spot) <= HERO_VISION_RANGE:
            return False
    return True


def patrol(hero, allies):
    def spot_score(spot):
        return sum(dist(spot, ally) for ally in allies if ally.id != hero.id) - dist(spot, hero) / 2

    role = get_role(hero)

    best_spot = max((spot for spot in spots if is_valid_spot(spot, hero, allies)), key=spot_score)
    if dist(best_spot, hero) > 2 * HERO_SPEED:
        return best_spot
    init_dir = get_direction(base, best_spot)
    random_theta = random() * pi - pi / 2
    dir_x, dir_y = rotate_vector(init_dir[0], init_dir[1], random_theta)
    x = RANDOM_SEARCH_RANGE[role] * dir_x + best_spot[0]
    y = RANDOM_SEARCH_RANGE[role] * dir_y + best_spot[1]
    return x, y


@wrapper_id
def get_role(hero_id):
    if is_tracking(hero_id):
        return TRACKER
    if hero_id % 3 in defenders_id:
        return DEFENDER
    return SCOUT


def scout(hero, hero_choice, heroes, ammo_spiders):
    # Default hero behavior
    global report
    spot = get_spot(hero.id)
    role = get_role(hero)
    targets = filter(lambda t: dist(spot, t) <= MAX_SPOT_RANGE[role], hero_choice)
    for target in targets:
        if not target.attackers or dist(hero, target) <= MAX_FARM_DIST:
            # If no threat get the wild mana by killing neutral spiders
            target.attackers.append(hero)
            return attack_spider(hero, target, hero_choice, ammo_spiders) + " farm %d" % target.id
    if is_tracking(hero):
        if hero_choice:
            return attack_spider(hero, hero_choice[0], hero_choice, ammo_spiders) + " trackattack"
        else:
            return move_to(spot) + " track"

    if current_objective[hero.id3] and is_valid_spot(current_objective[hero.id3][0], hero, heroes):
        objective, order = current_objective[hero.id3]
        if dist(objective, hero) >= HERO_SPEED:
            return order + " keepgoing"
    objective = clamp_to_map(patrol(hero, heroes))
    order = move_to(objective)
    current_objective[hero.id3] = (objective, order)
    return order + " newpatrol"

    # random_theta = random() * pi - pi / 2
    # dir_x, dir_y = get_spot_direction(hero_id)
    # random_dx, random_dy = rotate_vector(dir_x, dir_y, random_theta)
    # final_x = spot_x + random_dx * RANDOM_SEARCH_RANGE[SCOUT]
    # final_y = spot_y + random_dy * RANDOM_SEARCH_RANGE[SCOUT]
    # order = move_to(final_x, final_y) + " scout"
    # current_objective[hero_id] = clamp_to_map(final_x, final_y), order
    # return order


def debug_small(entity):
    return "id : {} x : {} y : {}\n".format(entity.id, entity.x, entity.y)


def is_attacking_base(spider):
    return bool(spider.threat_for == ALLY and spider.near_base)


def is_attacked(spider):
    return bool(spider.attackers)
    # for hero in spider.attackers:
    #     if get_role(hero) != TRACKER:
    #         return True
    # return False


# ----- Game Functions End ------ #


# --------- Main Loop --------- #
def main():
    global turn, report, mana, defenders_id, min_comfy_mana
    turn += 1
    # health: Your base health
    # mana: Spend ten mana to cast a spell
    my_health, my_mana = [int(j) for j in input().split()]
    min_comfy_mana = 0 if 30 * (220 - turn) <= my_mana else MIN_COMFY_MANA
    mana = my_mana
    # opponent_health, opponent_mana = [int(j) for j in input().split()]
    _ = input()  # ignore opponent_mana and opponent_health
    entity_count = int(input())  # Amount of heroes and spiders you can see
    entities = []
    # My heroes
    heroes = []
    # Spiders in the battlefield
    spiders = []
    # Enemy heroes
    enemy_heroes = []
    # Enemy heroes attacking us
    attackers = []
    # Spiders that are very dangerous
    critical_spiders = []

    entity_by_id = {}
    for i in range(entity_count):
        # _id: Unique identifier
        # _type: 0=spider, 1=your hero, 2=opponent hero
        # x: Position of this entity
        # shield_life: Count down until shield spell fades
        # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
        # health: Remaining health of this spider
        # vx: Trajectory of this spider
        # near_base: 0=spider with no target yet, 1=spider targeting a base
        # threat_for: Given this spider's trajectory, is it a threat to 1=your base,
        # 2=your opponent's base, 0=neither
        (_id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for) = \
            [int(j) for j in input().split()]
        entity = Entity(_id=_id, _type=_type, is_controlled=is_controlled, health=health, x=x, y=y, near_base=near_base,
                        threat_for=threat_for, vx=vx, vy=vy, shield_life=shield_life, attackers=[], id3=_id % 3)
        entities.append(entity)
        entity_by_id[_id] = entity
        if _type == 1:
            heroes.append(entity)
        elif _type == 0:
            spiders.append(entity)
            if is_critical(entity):
                critical_spiders.append(entity)
        else:
            enemy_heroes.append(entity)
            if dist(base, entity) <= TRACK_THRESHOLD:
                attackers.append(entity)
            else:
                untrack(entity)
    heroes_choices: list[list[Entity]] = [[]] * heroes_per_player
    heroes_secondary_choices: list[list[Entity]] = [[]] * heroes_per_player
    chosen = [10e10] * heroes_per_player
    orders = ["WAIT (Controlled)"] * heroes_per_player
    clean_tracking(heroes, enemy_heroes)
    # If no attack just farm
    if tracking == {}:
        defenders_id = [min(heroes, key=lambda h: dist(h, base)).id3]
    else:
        defenders_id = [0, 1, 2]

    for attacker in attackers:
        if not is_tracked(attacker):
            track(attacker, heroes)
        else:
            retrack(attacker, heroes)
    update_tracking(heroes)
    # Key : Spider, Value : enemies the spider will come across
    ammo_spiders = {}
    for tracker, attacker in tracking.items():
        # Add spiders that will pass near the attacker in the ammo_spiders dict
        key = target_cost_key(tracker, ammo_spiders)
        choice = critical_spiders.copy()
        choice.sort(key=key)
        heroes_choices[tracker.id3] = choice
        secondary = []
        for spider in spiders:
            second_point = spider.x + spider.vx, spider.y + spider.vy
            closest = closest_point_of_segment(spider, second_point, attacker, is_line_after=True)
            if dist(closest, attacker) <= ATTACKER_THRESHOLD:
                ammo_spiders.setdefault(spider, [])
                ammo_spiders[spider].append(attacker)
                secondary.append(spider)
        secondary.sort(key=key)
        heroes_secondary_choices[tracker.id3] = secondary

    # Enemies are sort by priority and distance for each hero
    defenders = []
    for hero in heroes:
        if is_tracking(hero):
            continue
        if hero.id3 in defenders_id:
            defenders.append(hero)
            # Only target spiders not too far away from the base if the hero is a defender
            choice = [s for s in spiders if dist(s, base) < MAX_DEFENDER_DISTANCE]
        else:
            choice = spiders.copy()
        choice.sort(key=target_cost_key(hero, ammo_spiders))
        heroes_choices[hero.id3] = choice
        heroes_secondary_choices[hero.id3] = choice

    # Sort hero by distance to their closest target so that no hero targets a spider that is closer to another
    heroes.sort(
        key=lambda h: dist(heroes_choices[h.id3][0], h) if len(heroes_choices[h.id3]) else INFINITY)

    # The heroes try to target different spiders
    scouting = []
    for i in range(heroes_per_player):
        hero = heroes[i]
        hero_id = hero.id % 3
        # if hero is controlled, he can't follow the orders, just skip it
        if hero.is_controlled:
            continue

        for choice in range(len(heroes_choices[hero_id])):
            spider_target: Entity = heroes_choices[hero_id][choice]
            # If the spider has a shield, target it
            # noinspection PyTypeChecker
            if spider_target.shield_life and is_attacking_base(spider_target):
                orders[hero_id] = attack_spider(hero, spider_target, spiders, ammo_spiders) + " P def %d" % \
                                  spider_target.id
                spider_target.attackers.append(hero)
                chosen[hero_id] = choice
                break

            if is_attacked(spider_target):
                for attacker in spider_target.attackers:
                    if not dist(attacker, spider_target) <= dist(spider_target, hero) and get_role(attacker) != TRACKER:
                        # Error, it's not supposed to happen
                        report += "\n/!\\ /!\\ /!\\/!\\ /!\\ /!\\/!\\ /!\\ /!\\ \n " \
                                  "ERROR at turn {}, spider {} is targeted by {} but {} is closer" \
                            .format(turn, spider_target.id, attacker.id, hero.id)
            else:
                # If no ally is already targeting the spider, we target it
                orders[hero_id] = attack_spider(hero, spider_target, spiders, ammo_spiders) + \
                                  (" T def %d" % spider_target.id if spider_target.threat_for == ALLY else
                                   " prev %d" % spider_target.id if spider_target in ammo_spiders.keys() else "")
                spider_target.attackers.append(hero)
                chosen[hero_id] = choice
                white_list_id = [heroes[k].id for k in range(i + 1)]

                # We sort the remaining heroes by distance to other spiders

                def sort_key(h):
                    # don't sort the heroes that are already targeting a spider
                    if h.id in white_list_id:
                        return [-INFINITY]
                    # sort the other heroes by their minimum target cost, spider_target excluded
                    h_choices = heroes_choices[h.id % 3]
                    cost_fun = target_cost_key(h, ammo_spiders)
                    if not h_choices:
                        return [INFINITY]
                    return min([INFINITY] if s == spider_target else cost_fun(s) for s in h_choices)

                # debug(list(map(sort_key, heroes)))
                heroes.sort(key=sort_key)
                break
        else:
            # If no spider is targeted, we scout
            scouting.append(hero)
    scouting.sort(key=lambda h: dist(h, patrol(h, heroes)))
    for hero in scouting:
        if is_tracking(hero):
            tracked: Entity = tracking[hero]
            tracked_dist = dist(tracked, hero)
            if tracked_dist > MAX_SPOT_RANGE[TRACKER]:
                debug(f"{hero.id} is tracking {tracked.id}")
                if mana > MIN_MANA_FOR_CONTROL_TRACKING and not tracked.shield_life and \
                        dist(tracked, base) < dist(hero, base):
                    if ceil(tracked_dist) + HERO_SPEED <= SPELL_RANGES[WIND]:
                        debug("wback info :", tracked.x, tracked.y, ceil(dist(tracked, hero)))
                        orders[hero.id3] = defense_wind(tracked, hero) + " WBACK"
                        continue
                    if ceil(tracked_dist) <= SPELL_RANGES[CONTROL] and not tracked.is_controlled:
                        orders[hero.id3] = control_entity(tracked, hero) + " COMEHERE"
                        continue
                orders[hero.id3] = move_to(tracked) + " tracking"
                continue
        orders[hero.id3] = scout(hero, heroes_secondary_choices[hero.id3], heroes,
                                 ammo_spiders)

    if report:
        debug(report)
    debug([f"{att.id} track {t.id}, dist:{int(dist(att, t))}/{TRACKER_RANGE}" for att, t in tracking.items()])
    debug("defenders", defenders_id)
    debug("ammos", [s.id for s in ammo_spiders.keys()])
    if critical_spiders:
        debug("critical spiders", [s.id for s in critical_spiders])
    for i in range(heroes_per_player):
        hero_id = i + 3 if heroes[0].id >= 3 else i
        debug("hero %d choice :" % hero_id,
              [s.id for s in heroes_choices[i]], [s.id for s in heroes_secondary_choices[i]])
        print("{} {}".format(orders[i],
                             "[%s%d]" % ("T" if is_tracking(hero_id) else "D" if i in defenders_id else "S", hero_id)))


while True:
    main()
