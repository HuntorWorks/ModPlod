import os
import sys
import time
from rich import print
from dotenv import load_dotenv
from obswebsocket import obsws, requests


class OBSWebsocketManager:

    def __init__(self):
        load_dotenv()
        self.websocket_ip = os.getenv("OBS_SERVER_HOST")
        self.websocket_port = os.getenv("OBS_SERVER_PORT")
        self.websocket_password = os.getenv("OBS_WEBSOCKET_PASSWORD")

        self.MAIN_SCENE = "SingleScreen"
        self.MAIN_SCENE_SOURCE_TO_ACTIVATE = "///Characters"
        self.CHARACTER_SOURCE_GROUP_NAME = "BarryCharacter"
        self.CHARACTER_TEXT_SOURCE = "Barry_Text"
        self.CHARACTER_TALK_MOVEMENT_SOURCE = "Character_Jaw"

        self.FONT_SCALING_RULES = [
            {"font_size": 250, "max_chars_per_line": 30, "max_msg_length": 200},            # 30 chars line break at 200 font 4 250 200 chars max
            {"font_size": 200, "max_chars_per_line": 35, "max_msg_length": 300},            # 35 chars line break at 150 font 4 200 250 chars max
            {"font_size": 150, "max_chars_per_line": 50}                                    # 50 chars line break at 150 font 500 chars-ish.. Looks good
        ]

        self.scene_list = []
        self.ws = obsws(self.websocket_ip, self.websocket_port, self.websocket_password)
        self.ws.connect()


    def get_scene_list(self):
        raw_scene_list = self.ws.call(requests.GetSceneList())
        for scene in raw_scene_list.getScenes():
            self.scene_list.append(scene['sceneName'])
        return self.scene_list

    def switch_scene(self, scene=None):
        self.ws.call(requests.SetCurrentProgramScene(sceneName=scene))

    def set_source_visibility(self, scene=None, source=None, visibilty=True):
        if not scene and not source:
            id_response = self.ws.call(requests.GetSceneItemId(sceneName=self.MAIN_SCENE, sourceName=self.MAIN_SCENE_SOURCE_TO_ACTIVATE))
        else:
            id_response = self.ws.call(requests.GetSceneItemId(sceneName=scene, sourceName=source))

        if "sceneItemId" not in id_response.datain:
            print(f"[red]ERROR[/red][white]: Could not find source item id for source [cyan]{source}[/cyan] in scene [cyan]{scene}[/cyan]!")
            return

        source_item_id = id_response.datain['sceneItemId']
        self.ws.call(requests.SetSceneItemEnabled(sceneName=self.MAIN_SCENE, sceneItemId=source_item_id, sceneItemEnabled=visibilty))

    def get_max_text_line_length(self, font_size):
        for rule in self.FONT_SCALING_RULES:
            for key, value in rule.items():
                if key == "font_size" and value == font_size:
                    return rule["max_chars_per_line"]
        return 50

    def set_dynamic_font_size(self, text):
        text_len = len(text)
        font_size = 0
        if text_len <= self.FONT_SCALING_RULES[0]["max_msg_length"]:
            font_size = self.FONT_SCALING_RULES[0]["font_size"]
        elif text_len <= self.FONT_SCALING_RULES[1]["max_msg_length"]:
            font_size = self.FONT_SCALING_RULES[1]["font_size"]
        else:
            font_size = self.FONT_SCALING_RULES[2]["font_size"]

        return font_size

    def text_wrap(self, text, font_size):
        max_line_length = self.get_max_text_line_length(font_size)
        words = text.split()
        lines = []

        current_line = ""

        for word in words:
            if len(current_line) + len(word) > max_line_length:
                lines.append(current_line.strip())
                current_line = ""
            current_line += word + " "

        lines.append(current_line.strip())
        return "\n".join(lines)

    def set_source_text(self, input_name, text_to_display, clear_text=False):
        if clear_text:
            print("Clearing Text!")
            self.clear_source_text(input_name) # clear any existing text

        response = self.ws.call(requests.GetInputSettings(inputName=input_name))
        current_settings = response.datain["inputSettings"]

        text_to_animate = f"{current_settings['text'].strip()} {text_to_display}"
        font_size = self.set_dynamic_font_size(text_to_animate)
        wrapped_text = self.text_wrap(text_to_animate, font_size)


        current_settings["text"] = wrapped_text
        current_settings["font"]["size"] = font_size

        self.ws.call(requests.SetInputSettings(
            inputName=input_name,
            inputSettings=current_settings
        ))

    def get_source_text(self, input_name):
        response = self.ws.call(requests.GetInputSettings(inputName=input_name))
        if "inputSettings" not in response.datain or "text" not in response.datain["inputSettings"]:
            print(f"[red]ERROR[/red][white]: Could not find source text for source [cyan]{input_name}[/cyan]!")
            return

        return response.datain['inputSettings']['text']

    def clear_source_text(self, input_name):
        self.ws.call(requests.SetInputSettings(
            inputName=input_name,
            inputSettings={"text": ""},
        ))

    def get_scene_item_id(self, scene_name, source_name):
        return self.ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name))

    def get_source_transform(self, scene_name, source_name):
        scene_item_id = self.get_scene_item_id(scene_name, source_name).datain["sceneItemId"]
        response = self.ws.call(requests.GetSceneItemTransform(sceneName=scene_name, sceneItemId=scene_item_id))

        return response

    def set_source_transform(self, scene_name, source_name, transform):
        # transform = {'sceneItemTransform': {
        #     'alignment': 5,
        #     'boundsAlignment':0,
        #     'boundsHeight': 0.0,
        #     'boundsType': 'OBS_BOUNDS_NONE',
        #     'boundsWidth': 0.0,
        #     'cropBottom': 0,
        #     'cropLeft': 0,
        #     'cropRight': 0,
        #     'cropToBounds': False,
        #     'cropTop': 0,
        #     'height': 59.0,
        #     'positionX': 46.0,
        #     'positionY': 186.0,
        #     'rotation': 0.0,
        #     'scaleX': 0.2236495316028595,
        #     'scaleY': 0.2234848439693451,
        #     'sourceHeight': 264.0,
        #     'sourceWidth': 2206.0,
        #     'width': 493.3708801269531
        # }}
 
        scene_item_id = self.get_scene_item_id(scene_name, source_name).datain['sceneItemId']
        self.ws.call(requests.SetSceneItemTransform(sceneName=scene_name, sceneItemId=scene_item_id, sceneItemTransform=transform))

    def get_input_source_settings(self, source_name):
        # EXAMPLE SETTINGS FOR A TEXT INPUT

        # settings = {'inputSettings': {
        #     'chatlog': False, 
        #     'chatlog_lines': 1, 
        #     'font': {
        #         'face': 'SMALLROSE', 
        #         'flags': 0, 
        #         'size': 400, 
        #         'style': 'Regular'
        #     }, 
        #     'gradient': False, 
        #     'outline': True, 
        #     'outline_color': 4278233855, 
        #     'outline_size': 19, 
        #     'text': 'Ducks fly upside down.'  
        #     }
        # }
        return self.ws.call(requests.GetInputSettings(inputName=source_name))

    def disconnect_websocket(self):
        self.ws.disconnect()
