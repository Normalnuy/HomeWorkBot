from aiogram.fsm.state import StatesGroup, State

class AddNewUser(StatesGroup):
    real_name = State()
    majnor = State()
    
class AddHomeWork(StatesGroup):
    homework_sub = State()
    homework_text = State()
    homework_data = State()
    
class EditHomeWork(StatesGroup):
    edit_sub = State()
    edit_text = State()
    
class NewState(StatesGroup):
    text = State()
