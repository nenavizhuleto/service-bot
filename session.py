from telebot import types, TeleBot
from __struct import Struct
from __locale import Locale


class Session:
    def __init__(self, chat: types.Chat, user: types.User, api: TeleBot, db, language) -> None:
        dbuser = db.get_user(user)
        if dbuser is None:
            self.user = user
            self.new = True
            self.locale = Locale.Get(language)
        else:
            self.user = dbuser
            self.new = False
            self.locale = Locale.Get(dbuser.language)

        self.__user = user
        self.chat = chat
        self.last_recieved_message = None
        self.state = None
        self.data = {}
        
        self.__api = api
        self.__db = db

    def change_locale(self, language):
        self.locale = Locale.Get(language)
        self.__db.update_user(self.__user, self.locale.language)

    def inter_text(self, text):
        if isinstance(self.user, Struct):
            text = text.replace('$username', '@' + self.user.username) \
                .replace('$role', vars(self.locale.roles)[self.user.role]) \
                .replace('$fullname', self.user.fullname)

        if 'order' in self.data.keys():
            order = self.data['order']
            text = text.replace('$order_type', order['type']) \
                .replace('$order_description', order['description'])

        return text

    def update_last_message(self, sent_message, template, keyboard=None):
        self.last_recieved_message = Struct(**{
            "id": sent_message.message_id,
            "text": sent_message.text,
            "template": template,
            "keyboard": keyboard,
            "type": sent_message.content_type
        })

    def send_message(self, text, keyboard=None, photo=None):
        template_text = text
        text = self.inter_text(text)

        if photo is None:
            sent_message = self.__api.send_message(self.chat.id, text, reply_markup=keyboard)
        else:
            sent_message = self.__api.send_photo(self.chat.id, photo, caption=text, reply_markup=keyboard)

        self.update_last_message(sent_message, template_text, keyboard)
        self.__db.save_message(sent_message)

    def send_last_message(self, photo=None):
        self.send_message(self.last_recieved_message.template, self.last_recieved_message.keyboard, photo=photo)

    def edit_message(self, text, keyboard=None, update=True):
        template_text = text
        text = self.inter_text(text)
        if self.last_recieved_message.type == 'photo':
            sent_message = self.__api.edit_message_caption(chat_id=self.chat.id, message_id=self.last_recieved_message.id, caption=text, reply_markup=keyboard)
        else:
            sent_message = self.__api.edit_message_text(chat_id=self.chat.id, message_id=self.last_recieved_message.id, text=text, reply_markup=keyboard)
        if update:
            self.update_last_message(sent_message, template_text, keyboard)
        self.__db.update_message(sent_message)

    def save_user(self, role):
        self.__db.save_user(self.__user, role, self.locale.language)

    def get_data(self, key):
        if key in self.data.keys():
            return self.data[key]
        return None

    def set_data(self, key, value):
        self.data[key] = value

    def clean_data(self):
        self.data = {}

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def update(self):
        self.user = self.__db.get_user(self.__user)


class SessionManager:
    def __init__(self, api, db, language='EN'):
        self.sessions = {}
        self.api = api
        self.db = db
        self.language = language

    def new(self, chat, user) -> Session:
        self.sessions[user.username] = self.create(chat, user)
        return self.sessions[user.username]

    def create(self, chat, user) -> Session:
        session = Session(chat, user, self.api, self.db, language=self.language)
        session.set_state('normal')
        return session

    def change_session_locale(self, session, language):
        if session.user.username not in self.sessions.keys():
            return None

        self.sessions[session.user.username].change_locale(language)


    def get(self, user) -> Session:
        if user.username not in self.sessions.keys():
            return None

        session = self.sessions[user.username]
        session.update()
        return session