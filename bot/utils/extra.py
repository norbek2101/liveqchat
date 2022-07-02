from telebot.handler_backends import State, StatesGroup


class MyStates(StatesGroup):
    start = State()
    help = State()


def login_required(func):
    def inner(message):
        
        return func(message)
    return func