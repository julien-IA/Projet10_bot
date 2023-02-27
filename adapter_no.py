from botbuilder.core import TurnContext, Middleware
from botbuilder.schema import Activity
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    TurnContext,
)

from helpers.UtteranceLog import UtteranceLog

class RecapMiddleware():
    def __init__(self, bot) -> None:
        self.bot=bot
    async def on_turn(self, turn_context: TurnContext, next):
        utterance_log = UtteranceLog()
        store_items = await utterance_log.storage.read(["UtteranceLog"])
        if "UtteranceLog" in store_items:
            utterance_log= store_items["UtteranceLog"]
            print(f"{utterance_log.turn_number}: "
                 f"The list_user is now: {','.join(utterance_log.utterance_list_user)} "
                 f"The list_bot is now: {','.join(utterance_log.utterance_list_bot)}")
                #  ci desosus il faut changer le test. On a tout ce qu'il faut maintenant dans les objets utterance_log
        if turn_context.activity.type == "message" and turn_context.turn_state.get('final_step'):
            print("RecapMiddleware", 'pouet')
            text = turn_context.activity.text.lower()
            print("text")
            if text == 'no':
                print("youhou!!!!!!!!!!!!!!!!")
                # Do something to redirect user to information gathering dialog
                await turn_context.send_activity("D'accord, veuillez fournir vos informations à nouveau.")
                # End the dialog with the option to restart
                await turn_context.send_activity("Vous pouvez taper 'restart' pour recommencer.")
                return
            else:
                print("dommage !!!!!!!!!!!!!!!!!")

        # Pass the turn on to the next middleware or the bot if this is the last middleware
        await next()
