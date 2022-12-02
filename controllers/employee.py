import keyboards
from controllers.__controller import Controller

class EmployeeController(Controller):
    def __init__(self, service) -> None:
        self.service = service


    def handle(self, session, callback):
        pass


    