import datetime
import math
import json
import requests
from ctypes import c_void_p, create_string_buffer
from time import sleep
from radar.process import Process
from radar.renderers import BaseRadar
from csgo.game_structures import Vector2, Entity
from csgo.bsptrace import BspTrace


class CSGORadar(object):
    renderers = {radar.config_name:radar for radar in BaseRadar.__subclasses__()}

    def __init__(self):
        self.config = json.loads(open("csgo/config.json", "r").read())
        offsets = requests.get(self.config['offsets_url'])
        offsets.raise_for_status()
        offsets = offsets.json()

        self.addresses = offsets['signatures']
        self.netvars = offsets['netvars']
        self.local_player = Entity()
        self.entities = [Entity() for i in range(64)]
        self.renderer = self.renderers[self.config['renderer']](self.config['radar'])
        self.bsp_tracer = BspTrace(self.config["game_path"])
        self.process = Process("Counter-Strike: Global Offensive")

        if self.process.get_module_size("client.dll") != offsets["modules"]["client.dll"]["size"]:
            print("client.dll size differs from the sigs, offsets might be outdated!")
        if self.process.get_module_size("engine.dll") != offsets["modules"]["engine.dll"]["size"]:
            print("engine.dll size differs from the sigs, offsets might be outdated!")

        self.client_dll = self.process.get_module_base("client.dll")
        self.engine_dll = self.process.get_module_base("engine.dll")

        print("Initiaded succesfully!")
        print("Offsets last updated on: {}".format(datetime.date.fromtimestamp(offsets['timestamp'])))

    def run(self):
        self.read(self.addresses)

        x_coords = []
        y_coords = []
        color = []
        visible = []

        center = Vector2(self.config['radar']['size'] / 2, self.config['radar']['size'] / 2)
        my_pos = Vector2.from_vec3(self.local_player.origin)

        for entity in self.entities:
            if entity.is_valid:
                enemy_pos = Vector2.from_vec3(entity.origin)
                enemy_pos = my_pos - enemy_pos

                distance = enemy_pos.length() * (0.02 * self.config['radar']['zoom'])

                distance = min(distance, self.config['radar']['size'] // 2)

                enemy_pos.normalize()
                enemy_pos *= distance

                enemy_pos += center

                if self.config['renderer'] == "pygame":
                    enemy_pos = self.rotate_point(enemy_pos, center, -self.local_player.angles.y)
                else:
                    enemy_pos = self.rotate_point(enemy_pos, center, -self.local_player.angles.y - 90)

                x_coords.append(enemy_pos.x)
                y_coords.append(enemy_pos.y)
                enemy = int(entity.team.value != self.local_player.team.value)
                color.append(enemy)
                if self.config['check_visibility'] and enemy:
                    visible.append(self.bsp_tracer.isVisible(self.local_player.origin, entity.origin))
                else:
                    visible.append(0)

        self.renderer.update(x_coords, y_coords, color, visible)

    def read(self, addresses):
        local_player_ptr = c_void_p()
        self.process.read_memory((self.client_dll + addresses['dwLocalPlayer']), local_player_ptr)
        if local_player_ptr.value is not None:
            self.local_player.update_info(self.process, local_player_ptr.value, self.netvars, True)
        else:
            self.local_player.update_info(None, None, None, False)

        client_state_ptr = c_void_p()
        map_path = create_string_buffer(128)
        self.process.read_memory(self.engine_dll + addresses['dwClientState'], client_state_ptr)
        self.process.read_memory(client_state_ptr.value + addresses['dwClientState_ViewAngles'], self.local_player.angles)
        self.process.read_memory(client_state_ptr.value + addresses['dwClientState_MapDirectory'], map_path)

        utf_map_path = map_path.value.decode('UTF-8')
        if utf_map_path != "" and utf_map_path != self.bsp_tracer.map_path:
            self.bsp_tracer.change_map(utf_map_path)

        entity_ptr = c_void_p()
        for i in range(64):
            self.process.read_memory((self.client_dll + addresses['dwEntityList']) + i * 16, entity_ptr)
            if entity_ptr.value is not None:
                self.entities[i].update_info(self.process, entity_ptr.value, self.netvars, True)
            else:
                self.entities[i].update_info(None, None, None, False)

    @staticmethod
    def rotate_point(to_rotate, center, angle, angle_in_radians=False):
        if not angle_in_radians:
            angle *= math.pi / 180

        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)

        result = Vector2(cos_theta * (to_rotate.x - center.x) - sin_theta * (to_rotate.y - center.y),
                         sin_theta * (to_rotate.x - center.x) + cos_theta * (to_rotate.y - center.y))

        result += center
        return result


if __name__ == "__main__":
    not_a_hack = CSGORadar()
    while True:
        not_a_hack.run()
        sleep(0.016)