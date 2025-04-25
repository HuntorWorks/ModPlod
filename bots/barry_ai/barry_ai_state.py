from core.constants import Mood

## INFO:  What do i want barry to respond to, and what do i want to be 'toggleable'
class BarryAIState :
    def __init__(self):
        self.muted = False
        self.current_mood = Mood.NEUTRAL

        self.pause_enabled = False
        
        # Events
        self.follow_events_enabled = True
        self.raid_events_enabled = True
        self.subscription_events_enabled = True

        # Moderation responses
        self.moderation_enabled = True
        self.timeout_enabled = True
        self.shoutout_enabled = True
    

        self.chat_responses_enabled = True

