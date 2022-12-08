import keyboards
from controllers.__controller import Controller

class CustomerController(Controller):
    def __init__(self, service) -> None:
        self.service = service


    


    def handle(self, session, callback):
        action = callback.data

        if session.get_state() == self.service.STATES[0]:
            match action:
                case 'new_order':
                    self.new_order(session, action)
                    
                case 'orders':
                    self.orders(session, action)

                case 'decline':
                    self.decline(session, action)
                
                case _:
                    self.order(session, action)

        elif session.get_state() == self.service.STATES[1]:
            text = vars(session.locale.orders.customer.new_order.text)

            if action == 'confirm':
                self.confirm(session, action)

            session.set_data('input_key', action)
            session.edit_message(text[action], update=False)


    def new_order(self, session, action):
        text = vars(session.locale.orders.customer.new_order.text)
        if session.get_data('order') is None:
            order = {
                "customer_id": str(session.user.id),
                "type": '',
                "photo": None,
                "description": '',
                "status": 'new'
            }
            session.set_data('order', order)

        session.edit_message(text[action], session.locale.orders.customer.new_order.keyboard)
        session.set_state(self.service.STATES[1])

    def orders(self, session, action):
        text = vars(session.locale.orders.customer.my_orders.text)
        statuses = vars(session.locale.statuses)
        orders = self.service.db.get_orders_by_user(session.user)
        orders_msg = f'\nTotal: {len(orders)}\nID\t\tType\t\tStatus\t\t\n\n'
        orders_markup = {}
        for order in orders:
            order_text = f'{order._id}\t\t{order.type}\t\t{statuses[order.status]}'
            orders_markup[f'{order._id}'] = order_text

        orders_markup['back'] = '<='
        
        session.edit_message(text[action] + orders_msg, keyboard=keyboards.make_kb(orders_markup))

    def decline(self, session, action):
        order = session.get_data('order')
        print(order)

    def order(self, session, action):
        order = self.service.db.get_order_by_id(action)
        session.set_data('order', order.__dict__)
        session.send_message(session.locale.orders.customer.my_orders.text.mo, keyboard=session.locale.orders.customer.order.keyboard, photo=order.photo)

    def confirm(self, session, action):
        text = vars(session.locale.orders.customer.new_order.text)
        order = session.get_data('order')
        if len(order['type']) == 0 or len(order['photo']) == 0 or len(order['description']) == 0:
            session.edit_message(text['no_invalid'], update=False)
            session.send_last_message()
            return

        self.service.db.save_order(order)
        session.edit_message(text[action], session.locale.menu.customer.keyboard)
        session.set_state(self.service.STATES[0])
        session.clean_data()
        return