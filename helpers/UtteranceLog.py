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
    
    def __new__(cls):
        if cls.__instance is None:
            print("création de l'instance du singleton UtteranceLog")
            cls.__instance = super().__new__(cls)
            cls.__instance.utterance_dict_turn      = {} 
            # cls.__instance.utterance_list_user      = []
            # cls.__instance.utterance_list_bot       = []
            cls.__instance.utterance_clear          = False
            cls.__instance.utterance_send           = False
            cls.__instance.utterance_list_intents   = []
            cls.__instance.utterance_list_entities  = []
            cls.__instance.utterance_yes_no         = 0
            cls.__instance.turn_nb                  = 0
        return cls.__instance
    
    def __init__(self):
        self.utterance_dict_turn        = UtteranceLog.__instance.utterance_dict_turn
        self.turn_nb                    = UtteranceLog.__instance.turn_nb
        # self.utterance_list_user        = UtteranceLog.__instance.utterance_list_user
        # self.utterance_list_bot         = UtteranceLog.__instance.utterance_list_bot
        self.utterance_clear            = UtteranceLog.__instance.utterance_clear
        self.utterance_send             = UtteranceLog.__instance.utterance_send
        self.utterance_list_intents     = UtteranceLog.__instance.utterance_list_intents
        self.utterance_list_entities    = UtteranceLog.__instance.utterance_list_entities
        self.utterance_yes_no           = UtteranceLog.__instance.utterance_yes_no
    
    async def set_utterance_clear(self, to_clear=False):
        self.utterance_clear=to_clear
        UtteranceLog.__instance = self
    
    async def set_utterance_send(self, to_send=False):
        self.utterance_send=to_send
        UtteranceLog.__instance = self

    # async def set_utterance_yes_no(self, Yes_No=""):
    #     if Yes_No=="Yes":
    #         self.utterance_yes_no+=1
    #     elif Yes_No=="No":
    #         self.utterance_yes_no-=1
    #     else :
    #         pass
    #     if(self.utterance_yes_no==-1):
    #         self.utterance_send=True
    #     UtteranceLog.__instance = self
    
    def set_utterance_values(self, intent, entities):
        self.utterance_list_intents.append(intent)
        self.utterance_list_entities.append(entities)
        UtteranceLog.__instance = self

    async def get_utterance_clear(self):
        return self.utterance_clear   

    async def get_utterance_send(self):
        return self.utterance_send


    async def store_utterance(self, utterance, is_bot=False, nb_bot=1):
        # print(utterance)
        conversation_list=[]
        if self.turn_nb > 0:
            conversation_list =  self.utterance_dict_turn[len(self.utterance_dict_turn)]
            if('Bot' in ''.join(conversation_list) and 'User' in ''.join(conversation_list) and is_bot):
                conversation_list=[]
                self.turn_nb+=1
            elif ('Bot' in ''.join(conversation_list) \
                  and ''.join(conversation_list).count('Bot')>=nb_bot and is_bot\
                    ):
                conversation_list=[]
                self.turn_nb+=1
        else :
            self.turn_nb=2         
            self.utterance_dict_turn[1]=[]

        if(is_bot) :
            conversation_list.append("Bot : " + utterance)
            self.utterance_dict_turn[self.turn_nb]=conversation_list
            # self.utterance_list_bot.append(utterance)
        else :
            for key, value in self.utterance_dict_turn.items():
                if('User' not in ''.join(value)):
                    self.utterance_dict_turn[key].append("User : " + utterance)
                    break
        
       
        print(self.utterance_dict_turn)
        UtteranceLog.__instance = self
    
    async def RAZ(self):        
        print("Suppression des données stockées")
        self.utterance_dict_turn.clear()
        self.turn_nb=0
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
        properties['turns'] = json.dumps(self.utterance_dict_turn)
        instrumentation_key:str = DefaultConfig.APPINSIGHTS_INSTRUMENTATION_KEY
        tc = TelemetryClient(instrumentation_key)                                    
        tc.track_trace(name=name, properties=properties)
        tc.flush()
        print("Insight envoyé !")
        await self.RAZ()
