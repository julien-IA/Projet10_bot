# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog
from datetime import datetime

class BookingDialog(CancelAndHelpDialog):
    """Flight booking implementation."""

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(BookingDialog, self).__init__(
            dialog_id or BookingDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client
        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.destination_step,
                self.origin_step,
                self.travel_date_step,
                self.return_date_step,
                self.verif_date_step,
                self.travel_max_cost_step,
                self.confirm_step,
                self.final_step,
            ],
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(text_prompt)
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            DateResolverDialog(DateResolverDialog.__name__, self.telemetry_client)
        )
        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for destination."""
        booking_details = step_context.options

        if booking_details.destination is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("To what city would you like to travel?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.destination)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.destination = step_context.result
        if booking_details.origin is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("From what city will you be travelling?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.origin)

    async def travel_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for travel date.
        This will use the DATE_RESOLVER_DIALOG."""

        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.origin = step_context.result
        if not booking_details.travel_date or self.is_ambiguous(
            booking_details.travel_date, None
        ) or not self.is_valid_date(booking_details.return_date):
            return await step_context.begin_dialog(
                DateResolverDialog.__name__, (booking_details.travel_date,1)
            )  # pylint: disable=line-too-long

        return await step_context.next(booking_details.travel_date)

    async def return_date_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for return date."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.travel_date = step_context.result
        if not booking_details.return_date or self.is_ambiguous(
            booking_details.return_date
        ) or not self.is_valid_date(booking_details.return_date):
            return await step_context.begin_dialog(
                DateResolverDialog.__name__, (booking_details.return_date,2)
            )  # pylint: disable=line-too-long

        return await step_context.next(booking_details.return_date)

    
    async def verif_date_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """ensure that the departure date is before the return date"""
        booking_details = step_context.options
        # Capture the response to the previous step's prompt
        booking_details.return_date = step_context.result

        if (self.is_depart_before_return(booking_details.travel_date,booking_details.return_date)):
            booking_details.return_date=None
            return await step_context.begin_dialog(
                DateResolverDialog.__name__, (booking_details.return_date,3)
            )  # pylint: disable=line-too-long

        return await step_context.next(booking_details.return_date)


    async def travel_max_cost_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for travel cost."""

        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.return_date = step_context.result
        if booking_details.max_cost is None :
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("What is the maximum price for this trip ?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.max_cost)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Confirm the information the user has provided."""
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.max_cost = step_context.result
        msg = (
            f"Please confirm, I have you traveling to: { booking_details.destination }"
            f" from: { booking_details.origin } from: { booking_details.travel_date} to: { booking_details.return_date }"
            f" for a maximum price of { booking_details.max_cost } $"
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg))
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction and end the dialog."""
        if step_context.result:
            booking_details = step_context.options
            booking_details.result = step_context.result

            return await step_context.end_dialog(booking_details)

        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types

    def is_depart_before_return(self, timex_depart: str, timex_return: str)->bool:
        """ensure that the departure date is before the return date"""
        d1 = datetime.strptime(timex_depart, "%Y-%m-%d")
        d2 = datetime.strptime(timex_return, "%Y-%m-%d")
        return d1 < d2

    def is_valid_date(self, timex: str)->bool:
        """ensure that the departure date is before the return date"""
        try:
            date = datetime.strptime(timex, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    