from telebot import TeleBot, types
from mongo import Mongo
from bson.objectid import ObjectId
import keyboards
from __struct import Struct
from session import SessionManager, Session

from controllers.customer import CustomerController
from controllers.admin import AdminController
from controllers.employee import EmployeeController


class Db():

    def __init__(self, connection_string, database_name) -> None:
        self.api = Mongo(connection_sting=connection_string).get_db(database_name)

    def save_message(self, message: types.Message):
        messages = self.api['messages']
        msg_document = {
            "chat_id": message.chat.id,
            "message_id": message.message_id,
            "user_id": message.from_user.id,
            "user_name": message.from_user.username,
            "text": message.text
        }
        return messages.insert_one(msg_document)

    def update_message(self, message):
        pass

    def save_user(self, user: types.User, role, language):
        users = self.api['users']
        user_document = {
            "id": user.id,
            "username": user.username,
            "fullname": user.full_name,
            "role": role,
            "language": language
        }
        return users.insert_one(user_document)

    def update_user(self, user, language):
        user = self.api['users'].update_one({"id": user.id}, { "$set": { 'language': language }})

    def save_order(self, order):
        orders = self.api['orders']
        # order_document = {
        #     "customer_id": order.customer_id,
        #     "type": order.type,
        #     "photos": order.photos,
        #     "description": order.description
        # }
        return orders.insert_one(order)

    def get_orders_by_user(self, user):
        _orders = self.api['orders'].find({ 'customer_id': user.id })
        orders = []
        for order in _orders:
            orders.append(Struct(**order))
        return orders

    def get_order_by_id(self, id):
        order = self.api['orders'].find_one({ "_id": ObjectId(id)})
        print(order)
        return self.check(order)

    def check(self, data):
        return None if data is None else Struct(**data)

    def get_user(self, user: types.User):
        user = self.api['users'].find_one({"id": user.id})
        return self.check(user)

    def get_one(self, collection, filter):
        document = self.api[collection].find_one(filter=filter)
        return self.check(document)


class Service():

    STATES = ['normal', 'input']



    def __init__(self, config) -> None:
        self.api = TeleBot(config.get('TELEGRAM_TOKEN'))
        self.db = Db(config.get('MONGO_CONNECTION_STRING'), config.get('MONGO_DB_NAME'))
        self.sm = SessionManager(self.api, self.db, language=config.get('LOCALE'))


        # Controllers
        self.admin_controller = AdminController(self)
        self.customer_controller = CustomerController(self)
        self.employee_controller = EmployeeController(self)

        # Callback registrations
        self.api.register_message_handler(self.welcome, commands=['start'])
        self.api.register_message_handler(self.register, commands=['register'])
        self.api.register_message_handler(self.change_locale, commands=['en', 'ru'])
        # self.api.register_message_handler(self.register_admin, commands=['register_admin'])
        self.api.register_message_handler(self.handle_new_order, func=lambda m: self.is_new_order(m))
        self.api.register_message_handler(self.handle_text, func=lambda m: self.sm.get(m.from_user).state == self.STATES[0])
        self.api.register_callback_query_handler(self.callback, None)



    def change_locale(self, message: types.Message):
        """
        Changes session language
        """
        session = self.sm.get(message.from_user)
        match message.text:
            case "/en":
                self.sm.change_session_locale(session, "EN")
            case "/ru":
                self.sm.change_session_locale(session, "RU")
        self.welcome(message)
    
    def exists(self, entity: str, filter: dict):
        """
        Checks if entity exists in database

        :return: True if exists
        :return: False if doesn't
        """
        return False if self.db.get_one(entity, filter) is None else True

    def handle_text(self, message: types.Message):
        """
        Handles unrecognized input from user
        :func: sends previous message sent to user
        """
        session = self.sm.get(message.from_user)
        session.send_last_message()

    def is_new_order(self, m):
        session = self.sm.get(m.from_user)
        if session.state == self.STATES[1] and 'order' in session.data:
            return True
        return False

    def handle_new_order(self, message: types.Message):
        session = self.sm.get(message.from_user)
        input_key = session.get_data('input_key')
        photo = session.get_data('order')['photo']
        if input_key != None:
            if message.content_type == 'photo':
                file = message.photo[-1].file_id
                session.get_data('order')[input_key] = file
                photo = file

            if message.content_type == 'text':
                session.get_data('order')[input_key] = message.text

        session.set_data('input_key', None)
        session.send_last_message(photo=photo)



    def welcome(self, message):
        session = self.sm.new(message.chat, message.from_user)
        if session.new:
            session.send_message(session.locale.welcome.text.unregistered)
        else:
            keyboard = None
            match session.user.role:
                case 'admin':
                    keyboard=session.locale.menu.admin.keyboard
                case 'customer':
                    keyboard=session.locale.menu.customer.keyboard
                case 'employee':
                    keyboard=session.locale.menu.employee.keyboard

            session.send_message(session.locale.welcome.text.registered, keyboard=keyboard)

    def register_admin(self, message):
        session = self.sm.new(message.chat, message.from_user)
        if self.exists('users', { 'role': 'admin'}):
            session.send_message("You're not an admin", keyboard=session.locale.back.keyboard)
        else:
            session.save_user('admin')
            session.send_message("You're now an admin", keyboard=session.locale.back.keyboard)

    def register(self, message):
        session = self.sm.new(message.chat, message.from_user)
        if session.new:
            session.save_user('customer')
            session.send_message("Registration complete", keyboard=session.locale.back.keyboard)
        else:
            session.send_message("You're already registered", keyboard=session.locale.back.keyboard)

    def callback(self, call: types.CallbackQuery):
        session = self.sm.get(call.from_user)
        print(call.data)

        if call.data == 'back' or session is None:
            session = self.sm.new(call.message.chat, call.from_user)
            keyboard = None
            match session.user.role:
                case 'admin':
                    keyboard=session.locale.menu.admin.keyboard
                case 'customer':
                    keyboard=session.locale.menu.customer.keyboard
                case 'employee':
                    keyboard=session.locale.menu.employee.keyboard
            session.send_message(session.locale.welcome.text.registered, keyboard)
            return

        match session.user.role:
            case 'admin':
                self.admin_controller.handle(session, call)
            case 'employee':
                self.employee_controller.handle(session, call)
            case 'customer':
                self.customer_controller.handle(session, call)


    def start(self):
        try:
            self.api.infinity_polling()
        except Exception as e:
            print(e)
