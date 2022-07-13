from telebot import types, TeleBot


def initializer_inline_query_handlers(_: TeleBot):
    @_.inline_handler(lambda query: True)
    def inline_query_handler(query: types.InlineQuery, bot=_):
        pass
