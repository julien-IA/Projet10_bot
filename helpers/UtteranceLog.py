from botbuilder.core import ActivityHandler, TurnContext, StoreItem, MemoryStorage
import logging
from applicationinsights import TelemetryClient, channel
from applicationinsights.logging import LoggingHandler
from opencensus.ext.azure.log_exporter import AzureLogHandler, AzureEventHandler
import json
from config_luis import DefaultConfig


class UtteranceLog(StoreItem):
    """
    Class for storing a log of utterances (text of messages) as a list.
    """
    __instance = None
    # __utterance_list_user = []
    # __utterance_list_bot = []
    # __utterance_clear = False
    # __utterance_send = False
    # __utterance_list_intent  = []
    # __utterance_list_entites = []
    
    def __new__(cls):
        if cls.__instance is None:
            print("création de l'instance du singleton UtteranceLog")
            cls.__instance = super().__new__(cls)
            cls.__instance.utterance_list_user = []
            cls.__instance.utterance_list_bot = []
            cls.__instance.utterance_clear = False
            cls.__instance.utterance_send = False
            cls.__instance.utterance_list_intents = []
            cls.__instance.utterance_list_entities = []
            cls.__instance.utterance_yes_no = 0
        return cls.__instance
    
    def __init__(self):
        self.utterance_list_user = (UtteranceLog.__instance.utterance_list_user)
        self.utterance_list_bot = UtteranceLog.__instance.utterance_list_bot
        self.utterance_clear = UtteranceLog.__instance.utterance_clear
        self.utterance_send = UtteranceLog.__instance.utterance_send
        self.utterance_list_intents = UtteranceLog.__instance.utterance_list_intents
        self.utterance_list_entities = UtteranceLog.__instance.utterance_list_entities
        self.utterance_yes_no = UtteranceLog.__instance.utterance_yes_no
    
    async def set_utterance_clear(self, to_clear=False):
        self.utterance_clear=to_clear
        UtteranceLog.__instance = self
    
    async def set_utterance_yes_no(self, Yes_No=""):
        if Yes_No=="Yes":
            self.utterance_yes_no+=1
        elif Yes_No=="No":
            self.utterance_yes_no-=1
        else :
            pass
        if(self.utterance_yes_no==-2):
            self.utterance_send=True
        UtteranceLog.__instance = self
    
    def set_utterance_values(self, intent, entities):
        self.utterance_list_intents.append(intent)
        self.utterance_list_entities.append(entities)
        UtteranceLog.__instance = self

    async def get_utterance_clear(self):
        return self.utterance_clear   

    async def get_utterance_send(self):
        return self.utterance_send


    async def store_utterance(self, utterance, is_bot=False):
        if(is_bot) :
            self.utterance_list_bot.append(utterance)
        else :
            self.utterance_list_user.append(utterance)

        UtteranceLog.__instance = self
    
    async def RAZ(self):        
        print("Suppression des données stockées")
        self.utterance_list_bot.clear()
        self.utterance_list_user.clear()
        self.utterance_list_user.clear()
        self.utterance_list_bot.clear()
        self.utterance_clear=False
        self.utterance_send = False
        self.utterance_list_intents.clear()
        self.utterance_list_entities.clear()
        self.utterance_yes_no=0
        UtteranceLog.__instance=self
    
    async def send_info(self):
        print("Envoi de l'insight")
        name=("Proposal rejected")
        properties={}
        properties['intent'] = self.utterance_list_intents
        properties['result'] = self.utterance_list_entities
        properties['bot']=self.utterance_list_bot
        properties['user']=self.utterance_list_user
        instrumentation_key:str = DefaultConfig.APPINSIGHTS_INSTRUMENTATION_KEY
        tc = TelemetryClient(instrumentation_key)                                    
        tc.track_trace(name=name, properties=properties)
        tc.flush()
        print("Insight envoyé !")
        await self.RAZ()
