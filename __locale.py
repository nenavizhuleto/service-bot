import keyboards
from __struct import Struct
from collections import namedtuple
from types import SimpleNamespace
import json


class Locale:

    

    def Get(language) -> None:

        locale = None
        with open(f'locale/{language.lower()}.json', 'r', encoding='UTF-8') as file:
            locale = json.load(file, object_hook=lambda d: Locale.__parse(d), )

        if locale is None:
            raise Exception('Couldn\'t load locale file!')

        locale.language = language

        

        return locale
        

    def __parse(obj: dict):
        if 'keyboard' in obj.keys():
            v = vars(obj['keyboard'])
            obj['keyboard'] = keyboards.make_kb(v)
        return SimpleNamespace(**obj)





def RU():
    locale = Locale()
    locale.roles = locale.Roles("Админ", "Клиент", "Работник")
    locale.statuses = locale.Statuses("Новый", "В работе")

    locale.welcome.text = locale.WelcomeText("Вы: $role\n\nВоспользуйтесь клавиатурой ниже для навигации", "Добро пожаловать!\n\nИспользуйте команду /register чтобы завершить регистрацию и начать пользоваться нашим сервисом.")
    locale.welcome.keyboard = locale.WelcomeKeyboard("Клиент", "Работник")

    mm_a_text = ""

    locale.main_menu.admin = locale.MainMenuAdmin("", "Настройки")

    return locale

    

def EN():
    ROLES = {
        "admin": "Admin",
        "employee": "Employee",
        "customer": "Customer"
    }
    STATES = ['normal', 'input']
    STATUSES = {
        'new': 'New',
        'progress': 'In progress'
    }

    WELCOME_KEYBOARD = keyboards.make_kb({"Employee": "welcome_employee", "Customer": "welcome_customer"}, row_width=3)
    WELCOME_TEXT = [
        "You are: $role\n\nUse keyboard below to navigate",
        "Welcome!\n\nUse /register command to complete the registration and start to utilize our services."
    ]
    BACK_KEYBOARD = keyboards.make_kb({'<=': "back"})

    # Admin keyboards
    # Main menu
    MM_A_KEYBOARD = keyboards.make_kb({"Settings": "admin_settings", "Services": "admin_services"})

    # Customer keyboards
    # Main menu
    MM_C_KEYBOARD = keyboards.make_kb({"My Orders": "customer_orders", "New Order": "customer_new_order"})
    # My orders
    O_C_Text = {
        "customer_orders": "List of your orders",
        "mo": "Your order:\n\nType: $order_type\n\nDescription: $order_description\n\n"
    }
    # New order
    NO_C_KEYBOARD = keyboards.make_kb({"Type": "no_type", "Photos": "no_photo", "Description": "no_description", "Confirm": "no_confirm"})
    NO_C_TEXT = {
        "customer_new_order": "Your order:\n\nType: $order_type\n\nDescription: $order_description\n\n",
        "no_type": "Please provide type of the order",
        "no_photo": "Please take photo of the device",
        "no_description": "Please describe your problem",
        "no_invalid": "You need to provide all information in respect to make an order!",
        "no_confirm": "Order is created successfully!"
    }
    # Employee keyboards
    # Main menu
    MM_E_KEYBOARD = keyboards.make_kb({"Customers": "employee_customers", "Orders": "employee_orders"})