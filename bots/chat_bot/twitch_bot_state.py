class TwitchBotState: 
    def __init__(self): 
        self.enabled = True
        #Moderation Commands
        self.general_command_permissions = { 
            "clip" : True,
            "followage" : True,  
        }
        self.moderation_command_permissions = {
            "so" : True,
            "title" : True,
            "game" : True,
            "ban" : True,
            "timeout" : True, 
            "unban" : True
        }