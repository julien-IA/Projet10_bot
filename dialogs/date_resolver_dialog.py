# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Handle date/time resolution for booking dialog."""

from datatypes_date_time.timex import Timex
from botframework.connector.models import ActionTypes #botframework.connector.models.ActionTypes
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from botbuilder.dialogs import WaterfallDialog, DialogTurnResult, WaterfallStepContext
from botbuilder.schema import SuggestedActions, CardAction
from botbuilder.dialogs.prompts import (
    DateTimePrompt,
    PromptValidatorContext,
    PromptOptions,
    DateTimeResolution,
    ConfirmPrompt,
)
from .cancel_and_help_dialog import CancelAndHelpDialog
from datetime import datetime
from helpers.UtteranceLog import UtteranceLog

class outils :
    def is_in_the_past(self, date):
        now = datetime.now().date()
        input_date = date.date()
        return (input_date<now)

    def return_before_departure(self, str_departure_date,str_return_date):
        d1 = datetime.strptime(str_departure_date, "%Y-%m-%d")
        d2 = datetime.strptime(str_return_date, "%Y-%m-%d")
        if(d2<d1):
            return True
        else:
            return False

    def is_a_date(self, str_date_to_test):
        try:
            date = datetime.strptime(str_date_to_test, "%Y-%m-%d")
            print(date)
            return True        
        except :
            return False
    

class DateResolverDialog(CancelAndHelpDialog):
    """Resolve the date"""

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(DateResolverDialog, self).__init__(
            dialog_id or DateResolverDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client

        date_time_prompt = DateTimePrompt(
            DateTimePrompt.__name__, DateResolverDialog.datetime_prompt_validator
        )
        date_time_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__ + "2", [self.initial_step, self.final_step]
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(date_time_prompt)
        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__ + "2"  

    async def initial_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for the date."""
        timex, step, date_start = step_context.options
        nb_wrong_answers=0
        if(step == 1):
            prompt_msg = "On what date would you like to depart?"
        if(step == 2):
            prompt_msg = "On what date would you like to return?"
        reprompt_msg = (
            "I'm sorry, for best results, please enter your travel "
            "date including the month, day and year."
        )

        if timex is None:
            # We were not given any date at all so prompt the user.
            
            utterance = prompt_msg
            utteranceLog = UtteranceLog()
            await utteranceLog.store_utterance(utterance, is_bot=True)

            return await step_context.prompt(
                DateTimePrompt.__name__,
                PromptOptions(  # pylint: disable=bad-continuation
                    prompt=MessageFactory.text(prompt_msg),
                    retry_prompt=MessageFactory.text(reprompt_msg),
                    validations={"date_start":date_start,"nb_wrong_answers":nb_wrong_answers}
                ),
            )
        
        return await step_context.next(DateTimeResolution(timex=timex))

    async def final_step(self, step_context: WaterfallStepContext):
        """Cleanup - set final return value and end dialog."""
        try:
            timex = step_context.result[0].timex
            return await step_context.end_dialog(timex)
        except:
            return await step_context.parent.cancel_all_dialogs()

    @staticmethod
    async def datetime_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        """ Validate the date provided is in proper form. """
        if prompt_context.context.activity.text == "Yes":
                is_ok=True
                return True
        is_ok=True
        un_outils = outils()
        if prompt_context.recognized.succeeded:
            timex = prompt_context.recognized.value[0].timex.split("T")[0]
            if is_ok==True :
                if un_outils.is_a_date(timex) :
                    date = datetime.strptime(timex, "%Y-%m-%d")
                else :
                    prompt_context.options.validations["nb_wrong_answers"]+=1
                    retry_prompt = prompt_context.options.retry_prompt.text
                    prompt=prompt_context.options.prompt.text
                    is_ok=False

            if is_ok==True :
                if un_outils.is_in_the_past(date):
                    prompt_context.options.validations["nb_wrong_answers"]+=1
                    retry_prompt = "We can't take you back in time. Please enter an upcoming date."
                    prompt =prompt_context.options.prompt.text
                    is_ok=False

            if is_ok==True :
                if prompt_context.options.validations["date_start"] != None :
                    if un_outils.return_before_departure(prompt_context.options.validations["date_start"], prompt_context.recognized.value[0].timex.split("T")[0]):
                        prompt_context.options.validations["nb_wrong_answers"]+=1
                        retry_prompt = "Please enter a departure date prior to the arrival date"
                        prompt =prompt_context.options.prompt.text
                        is_ok = False

            if is_ok==True :
                prompt_context.options.validations["nb_wrong_answers"]=0
            
        else :
            prompt_context.options.validations["nb_wrong_answers"]+=1
            retry_prompt= prompt_context.options.retry_prompt.text
            prompt=prompt_context.options.prompt.text
            is_ok=False


        if is_ok==False :
            utteranceLog = UtteranceLog()
            await utteranceLog.store_utterance(retry_prompt, is_bot=True,nb_bot=1)
            await prompt_context.context.send_activity(retry_prompt)

            await utteranceLog.store_utterance(prompt, is_bot=True,nb_bot=2)                        
            await prompt_context.context.send_activity(prompt)

        if prompt_context.options.validations["nb_wrong_answers"]>=2:
            suggested_actions=SuggestedActions(
                actions=[
                CardAction(
                        type=ActionTypes.im_back,
                        title="Yes",
                        value="Yes"
                        ),
                CardAction(
                        type=ActionTypes.im_back,
                        title="No",
                        value="No"
                        ),
                ]
            )
            if prompt_context.context.activity.text != "Yes" and prompt_context.context.activity.text != "No":
                reply_activity = MessageFactory.text("Do you need some Human help ?")
                reply_activity.suggested_actions = suggested_actions
                await prompt_context.context.send_activity(reply_activity)

            if prompt_context.context.activity.text == "Yes":
                is_ok=True
                return True
                
            elif prompt_context.context.activity.text == "No":             
                is_ok=False
                return False
                

            utteranceLog = UtteranceLog()
            prompt_context.options.validations["nb_wrong_answers"]=0
            await utteranceLog.store_utterance("Do you need some Human help ?", is_bot=True,nb_bot=1)
        
        return is_ok

