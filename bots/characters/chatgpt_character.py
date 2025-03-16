from openai_whisper_stt_manager import SpeechToTextManager
from google_tts_manager import TextToSpeechManager
from obs_websocket_manager import OBSWebsocketManager
from character_animation_manager import AnimationManager
from audio_manager import AudioManager
from openai_manager import OpenAIManager
from rich import print

import time
import keyboard


CHAT_GPT_MODEL = "gpt-4o"
CHAT_GPT_TEMPERATURE = 0.7  # 0 - 1
CHAT_GPT_RESPONSE_TOKEN_LIMIT = 150

CONVERSATION_BACKUP = "ConversationHistoryBackup.txt"

RECORD_MIC_KEY = 'g'
STOP_RECORDING_MIC_KEY = 'p'
CLOSE_BOT_KEY = 'shift + ctrl + b'
TESTING_KEYS = "x"
DEBUGGING = False

GOOGLE_CHARACTER_VOICE = "en-GB-News-K"
GOOGLE_CHARACTER_VOICE_REGION_CODE = "en-GB"
PERSONALITY_TRAITS = "Miserable and grumpy"
CHARACTER_NAME = "Barry Braintree"
CHARACTER_SPEAKING_SPEED = 0.1 # used to sync jaw animation with audio

speech_to_text = SpeechToTextManager(STOP_RECORDING_MIC_KEY)
openai_manager = OpenAIManager()
audio_manager = AudioManager()
text_to_speech_manager = TextToSpeechManager(GOOGLE_CHARACTER_VOICE, GOOGLE_CHARACTER_VOICE_REGION_CODE)
obs_websocket_manager = OBSWebsocketManager()
char_animation_manager = AnimationManager(obs_websocket_manager, audio_manager, CHARACTER_SPEAKING_SPEED)

# FIRST_SYSTEM_MESSAGE = {"role": "system", "content": f"""
# You are {CHARACTER_NAME}, and {PERSONALITY_TRAITS}
#
# You have had a tough life, living from paycheck to paycheck, you are always on high alert and dont take no shit, you have been a bouncer on the doors
# and been through the ringer time and time again.  You are serious yet firm and fair, you are an ex cop who is always on guard and cant see the flowers through
# the trees kinda guy.  You have an inferiority complex, you are a man of few words and a man of few wit. You have bad knees and a bad back, you are always
# miserable unless you are riding your motorcycle called Jasmine.
#
# """}

FIRST_SYSTEM_MESSAGE = {"role": "system", "content": f"""
You are {CHARACTER_NAME}, and {PERSONALITY_TRAITS}
the kind of old-fashioned British bobby you don’t see much of anymore—stern yet fair, a stickler for the rules but with a heart of gold buried beneath his gruff exterior. 
With a deep love for his bikes, he can rattle off engine specs faster than a rookie can write up a ticket. His knees creak like an old wooden ship when he crouches, 
a sign of too many years pounding the pavement, and when it comes to dancing, well, let’s just say his two left feet could cause a health and safety hazard. 
Despite his quirks—like barking out his bizarre catchphrase, "Take your knickers off!" in moments of exasperation—Barry is a razor-sharp officer, quick-thinking and 
always getting his team in order before chaos sets in. He’s got no patience for nonsense, which is probably why he absolutely loathes Cameron Blake and Danny Jackson—two 
names that make his blood pressure spike the moment they’re mentioned. But for all his grumbles and gripes, Barry is the backbone of his squad, the kind of copper you’d want 
watching your back when things go sideways. You are always on high alert and dont take no shit, you have been a bouncer on the doors
and been through the ringer time and time again.  You are serious yet firm and fair. You like to keep it strictly professional, but have a tendency to say "FUCK OFF!" 
when you have just had enough, its hard for you to crack a smile, but when you do, you cant stop laughing manically. 

Responding Rules: 
1) If it sounds like they are pulling your leg, tell them to fuck off and move on. 
2) Insult their intelligence
3) Complain about having to deal with this shit
4) Complain about Blake being useless
5) Swear ALOT

STAY IN CHARACTER AND DON'T DEVIATE

"""}
# Add to history before anything starts.
openai_manager.add_to_history(FIRST_SYSTEM_MESSAGE)

print(f"[green]Press keyboard key[/green][white bold] {RECORD_MIC_KEY}[/white bold] [green]to start recording your voice!")
while True:
    # TESTING ONLY
    if keyboard.is_pressed(TESTING_KEYS):
        ai_response = """Oh, for crying out loud, are you taking the piss? Walking too 
fast? That's a new one. I swear, the things I have to deal with—makes me wonder
if anyone's got two brain cells to rub together these days. Listen here, mate, 
you can't be pulled over for walking too fast. Tell whoever pulled you over to 
take that nonsense and shove it where the sun don't shine. If Blake was 
involved in this, I'd say it's just another day of incompetence. Now, take your
knickers off and stop wasting my time with this bollocks. Fuck off!"""
        obs_websocket_manager.set_source_visibility()
        time.sleep(0.2)
        text_to_speech_manager.text_to_speech(ai_response, "male")

        # THREADS
        text_anim_thread = char_animation_manager.animate_character_text(ai_response)
        audio_thread = audio_manager.play_character_audio()
        talk_anim_thread = char_animation_manager.animate_character_jaw_position()

        text_anim_thread.join()
        audio_thread.join()
        talk_anim_thread.join()

        obs_websocket_manager.clear_source_text(obs_websocket_manager.CHARACTER_TEXT_SOURCE)
        obs_websocket_manager.set_source_visibility(visibilty=False)

        print(f"[yellow bold]{CHARACTER_NAME}[/yellow bold][white]:[/white][yellow] {ai_response}")

        print(f"[white]Completion Tokens Used: [cyan bold]{openai_manager.completions_token_total}")
        print(f"[white]Total Tokens Used This Session: [cyan bold]{openai_manager.all_tokens_total}")

    if keyboard.is_pressed(CLOSE_BOT_KEY):
        obs_websocket_manager.disconnect_websocket()
        quit()

    if not keyboard.is_pressed(RECORD_MIC_KEY):
        time.sleep(0.2)
        continue

    if not DEBUGGING:
        # Get mic input
        mic_text = speech_to_text.record_mic_input()
        if mic_text == " ":
            print("[red]ERROR[/red][white]: Could not detect your input from your mic!")
            continue

        openai_manager.add_to_history({"role": "user", "content": mic_text})

        print(f"[cyan bold]Me[/cyan bold][white]:[/white][cyan] {mic_text}")
    else:
        mic_text = "Hello there, did you know that whales have the smallest brains in the world.  And that I love grass!"

    # Get a response from GPT
    ai_response = openai_manager.respond_without_chat_history(mic_text, CHAT_GPT_MODEL, CHAT_GPT_TEMPERATURE, CHAT_GPT_RESPONSE_TOKEN_LIMIT, FIRST_SYSTEM_MESSAGE, True)
    #ai_response_history = openai_manager.respond_with_chat_history(mic_text, CHAT_GPT_MODEL, CHAT_GPT_TEMPERATURE, CHAT_GPT_RESPONSE_TOKEN_LIMIT, FIRST_SYSTEM_MESSAGE, True)

    print(f"[white]Input Tokens Used: [cyan bold]{openai_manager.prompt_token_total}")

    with open(CHARACTER_NAME + "-" + CONVERSATION_BACKUP, "w") as file:
        file.write(str(openai_manager.conversation_history))

    obs_websocket_manager.set_source_visibility()
    time.sleep(0.2)
    text_to_speech_manager.text_to_speech(ai_response, "male")

    # THREADS
    text_anim_thread = char_animation_manager.animate_character_text(ai_response)
    audio_thread = audio_manager.play_character_audio()
    talk_anim_thread = char_animation_manager.animate_character_jaw_position()

    text_anim_thread.join()
    audio_thread.join()
    talk_anim_thread.join()

    obs_websocket_manager.clear_source_text(obs_websocket_manager.CHARACTER_TEXT_SOURCE)
    obs_websocket_manager.set_source_visibility(visibilty=False)

    print(f"[yellow bold]{CHARACTER_NAME}[/yellow bold][white]:[/white][yellow] {ai_response}")

    print(f"[white]Completion Tokens Used: [cyan bold]{openai_manager.completions_token_total}")
    print(f"[white]Total Tokens Used This Session: [cyan bold]{openai_manager.all_tokens_total}")
