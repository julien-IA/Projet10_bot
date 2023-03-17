# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from booking_details import BookingDetails
import json
from helpers.UtteranceLog import UtteranceLog

class Intent(Enum):
    BOOK_FLIGHT = "BookFlight"
    NONE_INTENT = "NoneIntent"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score
    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> tuple[Intent, object]:
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None
        
        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )
            # print("intent",intent,Intent.BOOK_FLIGHT.value)
            if intent == Intent.BOOK_FLIGHT.value:
                result = BookingDetails()
                # print("entities", recognizer_result.entities)
                # We need to get the result from the LUIS JSON which at every level returns an array.
                to_entities = recognizer_result.entities.get("$instance", {}).get(
                    "to", []
                )
                # print("to_entities", to_entities)
                if len(to_entities) > 0:
                    if recognizer_result.entities.get("to", [{"$instance": {}}])[0]:
                        to_entities = sorted(to_entities, key=lambda x: x['score'], reverse=True)
                        result.destination = to_entities[0]["text"].capitalize()
                    else:
                        result.destination = None
                        # result.unsupported_airports.append(
                        #     to_entities[0]["text"].capitalize()
                        # )
                # print("result.destination", result.destination)
                from_entities = recognizer_result.entities.get("$instance", {}).get(
                    "from", []
                )
                if len(from_entities) > 0:
                    # 
                    if recognizer_result.entities.get("from", [{"$instance": {}}])[0]:
                        from_entities = sorted(from_entities, key=lambda x: x['score'], reverse=True)
                        result.origin = from_entities[0]["text"].capitalize()
                    else:
                        result.origin=None
                        # result.unsupported_airports.append(
                        #     from_entities[0]["text"].capitalize()
                        # )
                # print("result.origin", result.origin)
                budget_entities = recognizer_result.entities.get("$instance", {}).get(
                    "budget", []
                )
                if len(budget_entities) > 0:
                    if recognizer_result.entities.get("budget", [{"$instance": {}}])[0]:
                        budget_entities = sorted(budget_entities, key=lambda x: x['score'], reverse=True)
                        result.max_cost = budget_entities[0]["text"]
                    else:
                        result.max_cost = None
                # print("budget_entities", budget_entities)
                # print("result.max_cost", result.max_cost)

                str_date_entities = recognizer_result.entities.get("$instance", {}).get(
                    "str_date", []
                )
                if len(str_date_entities) > 0:
                    if recognizer_result.entities.get("str_date", [{"$instance": {}}])[0]:
                        str_date_entities = sorted(str_date_entities, key=lambda x: x['score'], reverse=True)
                        result.travel_date = str_date_entities[0]["text"]
                    else:
                        result.travel_date = None
                # print("result.travel_date", result.travel_date)
                
                end_date_entities = recognizer_result.entities.get("$instance", {}).get(
                    "end_date", []
                )
                if len(end_date_entities) > 0:
                    if recognizer_result.entities.get("end_date", [{"$instance": {}}])[0]:
                        end_date_entities = sorted(end_date_entities, key=lambda x: x['score'], reverse=True)
                        result.return_date = end_date_entities[0]["text"]
                    else:
                        result.return_date = None
                # print("result.return_date", result.return_date)


                date_entities = recognizer_result.entities.get("datetime", [])
                # print("date_entities",date_entities)
                if date_entities:
                    if(date_entities[0]['type']=='daterange'):
                        # print('daterange')
                        date_str = date_entities[0]['timex'][0]
                        # extraire les deux dates à partir de la chaîne de caractères
                        timex_1, timex_2, _ = date_str.strip('()').split(',')
                        # print('timex_1', 'timex_2',timex_1, timex_2)                        
                    elif(date_entities[0]['type']=='date'):
                        # print('date')
                        timex_1=None
                        timex_2 = date_entities[0]['timex'][0]
                        # print('timex_2',timex_2)
                    else:
                        timex_1,timex_2=None,None
                    
                    if('X' in timex_1):
                        timex_1=None
                    
                    if('X'in timex_2):
                        timex_2=None

                    if(result.travel_date != None and result.return_date != None):
                        if(timex_1!=None and timex_2!=None): result.travel_date,result.return_date = timex_1, timex_2
                        else: result.travel_date,result.return_date=None,None
                    elif(result.return_date != None):
                        if(timex_1!=None and timex_2!=None): result.travel_date,result.return_date = timex_1, timex_2
                        else: result.travel_date,result.return_date=None,None
                    elif(result.travel_date != None):
                        if(timex_1!=None and timex_2!=None): result.travel_date,result.return_date = timex_1, timex_2
                        else: result.travel_date,result.return_date=None,None
                    else:
                        if(timex_1!=None and timex_2!=None): result.travel_date,result.return_date = timex_1, timex_2
                        else: result.travel_date,result.return_date=None,None

        except Exception as exception:
            print(exception)

        try:
            intent_json=json.dumps(recognizer_result.intents, default=lambda x: x.to_json())
            entities_json=json.dumps(recognizer_result.entities)
            print("intent = ", intent_json)        
            print("result = ", entities_json)

            utterance_log = UtteranceLog()
            utterance_log.set_utterance_values(intent=intent_json, entities=entities_json)
        except:
            pass
        return intent, result
