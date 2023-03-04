from botbuilder.core import TurnContext, Middleware
from botbuilder.schema import Activity
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    TurnContext,
)

# from applicationinsights import TelemetryClient, channel
# from applicationinsights.logging import LoggingHandler
# from opencensus.ext.azure.log_exporter import AzureLogHandler
# import logging

from helpers.UtteranceLog import UtteranceLog

class RecapMiddleware():
    def __init__(self, bot) -> None:
        self.bot=bot
    async def on_turn(self, turn_context: TurnContext, next):
        utterance_log = UtteranceLog()
        # store_items = await utterance_log.storage.read(["UtteranceLog"])
        # if "UtteranceLog" in store_items:
        #     utterance_log= store_items["UtteranceLog"]
            # print(f"{utterance_log.turn_number}: "
            #      f"The list_user is now: {','.join(utterance_log.utterance_list_user)} "
            #      f"The list_bot is now: {','.join(utterance_log.utterance_list_bot)}")
                #  ci desosus il faut changer le test. On a tout ce qu'il faut maintenant dans les objets utterance_log
        if len(utterance_log.utterance_list_bot)> 0:
            if turn_context.activity.type == "message" and 'Please confirm' in utterance_log.utterance_list_bot[-1]:
                text = turn_context.activity.text.lower()
                if text == 'no':
                    await turn_context.send_activity("We are sorry. Please try again.")
                    # On met à jour les variables UtteranceLog
                    await utterance_log.set_utterance_yes_no("No")

                    # # On envoie un insight
                    # from opencensus.ext.azure.log_exporter import AzureEventHandler

                    # logger = logging.getLogger(__name__)
                    # logger.addHandler(AzureEventHandler(connection_string='InstrumentationKey=7098a1af-175f-4486-bcd1-8d161bda590e'))
                    # logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
                    # logger.critical
                    # # On réinitialise l'enregistrement de la conversation
                    # print("on détruit l'objet utterance")
                    # await utterance_log.RAZ()
                else :
                    await utterance_log.set_utterance_yes_no("Yes")
                    await utterance_log.set_utterance_clear(True)


                                   

        # Pass the turn on to the next middleware or the bot if this is the last middleware
        await next()
