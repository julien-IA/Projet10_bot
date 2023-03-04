import unittest
import aiounittest

from botbuilder.core import (
    TurnContext,
    ConversationState,
    MemoryStorage,
    MessageFactory
)

from botbuilder.schema import Activity, ActivityTypes, Attachment
from botbuilder.dialogs import DialogSet, DialogTurnStatus
from botbuilder.core.adapters import TestAdapter
from botbuilder.dialogs.prompts import (
    DateTimePrompt,
    PromptValidatorContext,
    PromptOptions,
    DateTimeResolution,
)

class DialogTests(aiounittest.AsyncTestCase):
    async def test_dialog(self):

        async def exec_test(turn_context:TurnContext):
            dialog_context = await dialogs.create_context(turn_context)
            results = await dialog_context.continue_dialog()
            if (results.status == DialogTurnStatus.Empty):
                dialog_context.options = booking_details
                await dialog_context.begin_dialog("MainDialog")
            elif results.status == DialogTurnStatus.Complete:
                reply = results.result
                await turn_context.send_activity(reply)
            await conversation_state.save_changes(turn_context)

        ma_config = DefaultConfig()
        booking_details = BookingDetails()
        adapter = TestAdapter(exec_test)

        conversation_state = ConversationState(MemoryStorage())
        dialogs_state = conversation_state.create_property("dialog_state")
        dialogs = DialogSet(dialogs_state)
        dialogs.add(MainDialog(FlightBookingRecognizer(ma_config), BookingDialog()))

        step1 = await adapter.test("Hello", "What can I help you with today ?", timeout=30000)
        step2 = await step1.send('I want to book a fly.')
        step3 = await step2.assert_reply('To what city would you like to travel?')
        step4 = await step3.send('I want to go to London.')
        step5 = await step4.assert_reply('From what city will you be travelling ?')
        step6 = await step5.send('I want to start from Paris.')
        step7 = await step6.assert_reply('On what date would you like to depart?')
        step8 = await step7.send('From 25/07/2023')
        step9 = await step8.assert_reply('On what date would you like to return?')
        step8 = await step7.send('From 01/08/2023')
        step9 = await step8.assert_reply('What is the maximum price for this trip ?')
if __name__ == '__main__':
    from config_luis import DefaultConfig
    from dialogs import MainDialog
    from dialogs import BookingDialog
    from booking_details import BookingDetails
    from flight_booking_recognizer import FlightBookingRecognizer
    unittest.main()