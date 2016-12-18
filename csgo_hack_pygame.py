# TODO: Maybe turn all of this into a class instead of a script with a while true loop?
# TODO: Config file
import Process
import requests
import datetime
import math
import os
from game_structures import Vector2, Entity
from time import sleep
from ctypes import c_void_p, create_string_buffer
from renderers import PyGameRadar
from bsptrace import BspTrace


CHECK_VISIBILITY = False
RADAR_SIZE = 400
ZOOM = 10
GAME_PATH = os.path.join("C:\\", "Program Files (x86)", "Steam",
                         "steamapps", "common", "Counter-Strike Global Offensive",
                         "csgo") #lul

#offsets = json.loads(open("data/offsets.json", "r").read())
offsets = requests.get("https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.json").json()

print("Offsets last updated on: {}".format(datetime.date.fromtimestamp(offsets['timestamp'])))

addresses = offsets['signatures']
netvars = offsets['netvars']

addr_local_player = addresses['dwLocalPlayer']
addr_entity_list = addresses['dwEntityList']

csgo_process = Process.Process("Counter-Strike: Global Offensive")

client_dll = csgo_process.get_module_base("client.dll")
engine_dll = csgo_process.get_module_base("engine.dll")

local_player_ptr = c_void_p()
client_state_ptr = c_void_p()
csgo_process.read_memory((client_dll + addr_local_player), local_player_ptr)

local_player = Entity()

entities = [Entity() for i in range(64)]

renderer = PyGameRadar(RADAR_SIZE, "My PyGame Game")

map_path = create_string_buffer(128)

bsp_tracer = BspTrace(GAME_PATH)

def rotate_point(to_rotate, center, angle, angle_in_radians=False):
    if not angle_in_radians:
        angle *= math.pi / 180

    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)

    result = Vector2(cos_theta * (to_rotate.x - center.x) - sin_theta * (to_rotate.y - center.y),
                     sin_theta * (to_rotate.x - center.x) + cos_theta * (to_rotate.y - center.y))

    result += center
    return result

while True:
    local_player.update_info(csgo_process, local_player_ptr.value, netvars, True)

    csgo_process.read_memory(engine_dll + addresses['dwClientState'], client_state_ptr)
    csgo_process.read_memory(client_state_ptr.value + addresses['dwClientState_ViewAngles'], local_player.angles)
    csgo_process.read_memory(client_state_ptr.value + addresses['dwClientState_MapDirectory'], map_path)

    utf_map_path = map_path.value.decode('UTF-8')
    if utf_map_path != "" and  utf_map_path != bsp_tracer.map_path:
        bsp_tracer.change_map(utf_map_path)

    entity_ptr = c_void_p()

    for i in range(64):
        csgo_process.read_memory((client_dll + addr_entity_list) + i * 16, entity_ptr)
        if entity_ptr.value is not None:
            entities[i].update_info(csgo_process, entity_ptr.value, netvars, True)
        else:
            entities[i].update_info(None, None, None, False)

    x_coords = []
    y_coords = []
    color = []
    visible = []

    center = Vector2(RADAR_SIZE / 2, RADAR_SIZE / 2)
    my_pos = Vector2.from_vec3(local_player.origin)

    for entity in entities:
        if entity.is_valid:
            enemy_pos = Vector2.from_vec3(entity.origin)
            enemy_pos = my_pos - enemy_pos

            distance = enemy_pos.length() * (0.02 * ZOOM)

            distance = min(distance, RADAR_SIZE // 2)

            enemy_pos.normalize()
            enemy_pos *= distance

            enemy_pos += center

            enemy_pos = rotate_point(enemy_pos, center, -(local_player.angles.y))

            x_coords.append(enemy_pos.x)
            y_coords.append(enemy_pos.y)
            enemy = int(entity.team.value != local_player.team.value)
            color.append(enemy)
            if CHECK_VISIBILITY and enemy:
                visible.append(bsp_tracer.isVisible(local_player.origin, entity.origin))
            else:
                visible.append(0) # Only check for enemies because the code is very expensive to run

    renderer.update(x_coords, y_coords, color, visible)
    sleep(0.0080) # Should give about 120fps for dat smooth hacking
