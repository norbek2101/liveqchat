CHAT_ID_FOR_NOTIFIER = -1001

class LANGUAGE:
    UZ = '0'
    RU = '1'
    EN = '2'

    DICT = {
        UZ: "O'zbekcha",
        RU: "Русский",
        EN: "English"
    }

    CHOICE = DICT.items()


class STEP:
    MAIN = 0

    GETTING_POST_MESSAGE = 1


class CALLBACK:
    SET_LANGUAGE = 0


class REASONS:
    GENERAL = '0'
    API_EXCEPTION_ON_CALLBACK_QUERY_HANDLER = '1'
    EXCEPTION_ON_CALLBACK_QUERY_HANDLER = '2'

    DICT = {
        GENERAL: "General Error",
        API_EXCEPTION_ON_CALLBACK_QUERY_HANDLER: "ApiException on callback_query_handler",
        EXCEPTION_ON_CALLBACK_QUERY_HANDLER: "Exception on callback_query_handler"
    }

    CHOICE = DICT.items()


class CONSTANT:
    TOKEN = '4'

    DEFAULT = {
        TOKEN: ""
    }

    DICT = {
        TOKEN: "TOKEN"
    }

    CHOICES = DICT.items()


class MESSAGE:

    class TYPE:
        TEXT = '0'
        PHOTO = '1'
        AUDIO = '2'
        VOICE = '3'
        VIDEO = '4'

        DICT = {
            TEXT: "Matnli xabar",
            PHOTO: "Fotosuratli xabar",
            AUDIO: "Audio xabar",
            VOICE: "Ovozli xabar",
            VIDEO: "Video xabar"
        }

        CHOICES = DICT.items()


class Text:
    WELCOME = """Assalom alekum, Livegram botimizga xush kelibsiz!
<b>Foydalish uchun:</b>
/start - Tizimni qayta ishga tushirish.
/register - Registratsiyadan o'tish.
/newbot - Yangi bot qo'shish.
/mybots -Men yaratgan botlar.
/help - Botdan yordam olish.
Aloqa uchun: (99)640-55-99"""
    HELP = """ Qo'shimcha ma'lumotlar.
Livegram botimizga xush kelibsiz!

<b>Foydalish uchun:</b>
/start - Tizimni qayta ishga tushirish.
/mybots -Men yaratgan botlar
Aloqa uchun: (99)640-55-99"""
    NOT_REGISTERED = """Siz ro'yhatdan o'tmagansiz.
Ro'yhatdan o'tib oling.
Registratsiydan o'tish -- /register"""
    ALREADY_REGISTER = "Siz avval ro'yhatdan o'tgansiz."
    PHONE_NUMBER = 'Telefon raqamingizni kiriting'
    FIRST_NAME = 'Ismingizni kiriting'
    LAST_NAME = 'Familiyangizni kiriting'
    CONTACT_NOT_VALID = "Shahsiy telefon raqamingizni kiriting"
    NEWBOT = '''Botni ulash uchun quyidagi qadamlarni bajaring:
1. @BotFather ni oching va yangi bot yarating.
2. Tokenni olganizdan keyin shu yerga tokenni kiriting.'''

    INVALID_TOKEN = "Xato token kiritdingiz,\n"\
"Iltimos tokenni tekshirib qaytadan yuboring. "
    ENTER_TOKEN = "Bot tokenini kiriting!"
    BOT_ALREADY_CREATED = "Bu bot allaqachon ulangan, @botfather yordamida"\
"boshqa bot yaratib o'shaning tokenini yuboring."
    BOT_CREATED = """
Bot yaratish yakunlandi.
Yordam kerak bo'lsa,
/help -- tugmasini bosing.
"""
    BOT_LIST = "Botlaringiz ro'yxati"
    BOTS_NOT_FOUND = """Botlar mavjud emas
Yangi bot yaratish /newbot
"""




class BtnText:
    BTN_PHONE_NUMBER = "Telefon raqamni jo'natish"


SLAVE_BOT_COMMANDS = [
    {
        "command": 'start',
        "description": "Foydalanishni boshlash"
    },
]

MAIN_BOT_COMMANDS = [
    {
        "command": 'start',
        "description": "Foydalanishni boshlash"
    },
    {
        "command": 'register',
        "description": "Ro'yxatdan o'tish"    
    },
    {
        "command": 'newbot',
        "description": "Yangi bot yaratish"
    },
    {
        "command": 'mybots',
        "description": "Mening botlarim"
    },
    {
        "command": 'help',
        "description": "Yordam"
    },
]