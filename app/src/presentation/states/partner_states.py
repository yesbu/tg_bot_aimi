from aiogram.fsm.state import State, StatesGroup


class PartnerRegistrationStates(StatesGroup):
    waiting_for_center_name = State()
    waiting_for_center_city = State()
    waiting_for_center_address = State()
    waiting_for_center_phone = State()
    waiting_for_center_description = State()


class TeacherManagementStates(StatesGroup):
    waiting_for_teacher_name = State()
    waiting_for_teacher_phone = State()
    waiting_for_teacher_subject = State()


class CourseManagementStates(StatesGroup):
    waiting_for_course_name = State()
    waiting_for_course_category = State()
    waiting_for_course_description = State()
    waiting_for_course_schedule = State()
    waiting_for_course_price_4 = State()
    waiting_for_course_price_8 = State()
    waiting_for_course_price_unlimited = State()
    waiting_for_course_age_min = State()
    waiting_for_course_age_max = State()
