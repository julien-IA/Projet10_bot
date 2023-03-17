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
        if len(utterance_log.utterance_dict_turn)> 0:
            # print("utterance_log.utterance_dict_turn = ", utterance_log.utterance_dict_turn)
            if turn_context.activity.type == "message" and 'Please confirm' in ''.join(utterance_log.utterance_dict_turn[len(utterance_log.utterance_dict_turn)]):
                text = turn_context.activity.text.lower()
                if text == 'no':
                    await turn_context.send_activity("We are sorry. Please try again.")
                    await utterance_log.store_utterance("We are sorry. Please try again.",is_bot=True)
                    # On met à jour les variables UtteranceLog
                    await utterance_log.set_utterance_send(True)
                    await utterance_log.set_utterance_clear(True)

            if turn_context.activity.type == "message" and 'Do you need some Human help ?' in ''.join(utterance_log.utterance_dict_turn[len(utterance_log.utterance_dict_turn)]):
                text = turn_context.activity.text.lower()
                if text == 'yes':
                    msg="We are sorry that we cannot properly respond to your request. For a quick processing of your request please send us an email to contact@flyme.com"
                    await turn_context.send_activity(msg)
                    await utterance_log.store_utterance(msg,is_bot=True, nb_bot=1)
                    # On met à jour les variables UtteranceLog
                    await utterance_log.set_utterance_send(True)
                    await utterance_log.set_utterance_clear(True)                      

        # Pass the turn on to the next middleware or the bot if this is the last middleware
        await next()
