from botbuilder.core import ActivityHandler, TurnContext, StoreItem, MemoryStorage

class UtteranceLog(StoreItem):
    """
    Class for storing a log of utterances (text of messages) as a list.
    """
    __instance = None
    __memory_storage = None
    __turn_number = 0
    __utterance_list_user = []
    __utterance_list_bot = []
    
    def __new__(cls):
        if cls.__instance is None:
            print("création de l'instance du singleton UtteranceLog")
            cls.__instance = super().__new__(cls)
        return cls.__instance
    
    def __init__(self):
        if not UtteranceLog.__memory_storage:
            print("création de l'objet mémoire")
            UtteranceLog.__memory_storage = MemoryStorage()
        self.storage = UtteranceLog.__memory_storage
        self.utterance_list_user = UtteranceLog.__utterance_list_user
        self.utterance_list_bot = UtteranceLog.__utterance_list_bot
        self.turn_number = UtteranceLog.__turn_number
        self.e_tag = "*"

    async def store_utterance(self, utterance, is_bot=False):
        if(is_bot) :
                if self.utterance_list_bot==[]:
                    print("store bot vide")
                    # Create a new state object with the first utterance
                    self.utterance_list_bot.append(utterance)
                else:
                    print("store avec quelque chose")
                    # Add the new utterance to the existing state object
                    print("utterance_log.utterance_list_bot",self.utterance_list_bot)
                    self.utterance_list_bot.append(utterance)
        else :
            if self.utterance_list_user==[]:
                print("store user vide")
                # Create a new state object with the first utterance
                self.utterance_list_user.append(utterance)
                self.turn_number = 1
            else:
                print("store user avec quelque chose")
                # Add the new utterance to the existing state object
                print("utterance_log.utterance_list_user",self.utterance_list_user)
                self.utterance_list_user.append(utterance)
                self.turn_number += 1


        UtteranceLog.__utterance_list_user = self.utterance_list_user
        UtteranceLog.__utterance_list_bot = self.utterance_list_bot
        # Save the state object to your storage
        changes = {"UtteranceLog": self}
        UtteranceLog.__turn_number = self.turn_number
        await UtteranceLog.__memory_storage.write(changes)
