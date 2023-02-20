from botbuilder.core import TurnContext, Middleware
from botbuilder.schema import Activity

class RecapMiddleware(Middleware):
    async def on_turn(self, turn_context: TurnContext, next):
        print("RecapMiddleware")
        print(turn_context.activity.type)
        print(turn_context.turn_state)
        if turn_context.activity.type == "message": #and turn_context.turn_state.get('final_step'):
            print("RecapMiddleware", 'pouet')
            text = turn_context.activity.text.lower()
            print("text")
            if text == 'no':
                print("youhou!!!!!!!!!!!!!!!!")
                # Do something to redirect user to information gathering dialog
                await turn_context.send_activity("D'accord, veuillez fournir vos informations à nouveau.")
                # End the dialog with the option to restart
                await turn_context.send_activity("Vous pouvez taper 'restart' pour recommencer.")
                return
            else:
                print("dommage !!!!!!!!!!!!!!!!!")

        # Pass the turn on to the next middleware or the bot if this is the last middleware
        await next()
