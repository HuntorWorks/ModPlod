from bots.gpt_character import Character
import keyboard
import time
CLOSE_BOT_KEY = 'x'
RECORD_MIC_KEY = 'g'
STOP_RECORDING_KEY = 'p'

barry = Character(character_name="Barry Braintree")

def handle_ai_interaction_from_user(character):
        if not keyboard.is_pressed(RECORD_MIC_KEY):
            time.sleep(0.2)
            return

        user_mic_input = character.handle_mic_input(STOP_RECORDING_KEY)
        character.add_to_chat_history(user_msg=user_mic_input)
        ai_response = character.get_gpt_string_response(user_mic_input)
        character.add_to_chat_history(ai_response=ai_response)
        character.speak(ai_response)



while True:
    if keyboard.is_pressed(CLOSE_BOT_KEY):
        quit()

    handle_ai_interaction_from_user(barry)

print("FINITO")