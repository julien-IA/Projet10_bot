import unittest
import aiounittest
import asyncio

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

from config_luis import DefaultConfig
from dialogs import MainDialog
from dialogs import BookingDialog
from booking_details import BookingDetails
from flight_booking_recognizer import FlightBookingRecognizer


class DialogTests(aiounittest.AsyncTestCase):

    @classmethod
    def setUpClass(cls):
        # Lancer l'application ici
        cls.loop = asyncio.get_event_loop()
        cls.app = cls.loop.run_until_complete(cls.start_app())

    @classmethod
    async def start_app(cls):
        ma_config = DefaultConfig()
        booking_details = BookingDetails()
        adapter = TestAdapter(cls.exec_test)

        conversation_state = ConversationState(MemoryStorage())
        dialogs_state = conversation_state.create_property("dialog_state")
        cls.dialogs = DialogSet(dialogs_state)
        cls.dialogs.add(MainDialog(FlightBookingRecognizer(ma_config), BookingDialog()))

        return {"adapter": adapter, "conversation_state": conversation_state}

    async def test_dialog(self):
        # Utiliser l'application ici
        step1 = await self.app["adapter"].test("Hello", "What can I help you with today ?", timeout=30000)
        step2 = await step1.send('I want to book a fly.')
        step3 = await step2.assert_reply('To what city would you like to travel ?')
        step4 = await step3.send('I want to go to London.')
        step5 = await step4.assert_reply('From what city will you be travelling ?')
        step6 = await step5.send('I want to start from Paris.')
        step7 = await step6.assert_reply('On what date would you like to depart?')
        step8 = await step7.send('25/06/2023')
        step9 = await step8.assert_reply('On what date would you like to return?')
        step8 = await step7.send('30/06/2023')
        step9 = await step8.assert_reply('What is the maximum price for this trip ?')

    @classmethod
    async def exec_test(cls, turn_context: TurnContext):
        dialog_context = await cls.dialogs.create_context(turn_context)
        results = await dialog_context.continue_dialog()
        if results.status == DialogTurnStatus.Empty:
            dialog_context.options = BookingDetails()
            await dialog_context.begin_dialog("MainDialog")
        elif results.status == DialogTurnStatus.Complete:
            reply = results.result
            await turn_context.send_activity(reply)
        await cls.app["conversation_state"].save_changes(turn_context)

    @classmethod
    def tearDownClass(cls):
        # Arrêter l'application ici
        # cls.loop.run_until_complete(cls.app["conversation_state"].storage.delete())
        # cls.loop.run_until_complete(cls.app["conversation_state"].save_changes())
        cls.loop.close()


if __name__ == '__main__':
    unittest.main()
