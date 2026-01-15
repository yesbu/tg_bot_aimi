from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from dishka import FromDishka

from src.infrastructure.persistence.repositories import CityRepository
from src.presentation.bot.states.partner_states import PartnerRegistrationStates


router = Router()


@router.callback_query(F.data.startswith("city_"), PartnerRegistrationStates.waiting_for_center_city)
async def city_selected_for_center(
    callback: CallbackQuery,
    state: FSMContext,
    city_repo: FromDishka[CityRepository]
):
    city_id = int(callback.data.replace("city_", ""))
    
    cities = await city_repo.get_all_cities()
    city_name = next((name for id, name in cities if id == city_id), None)
    
    if not city_name:
        await callback.answer("Город не найден", show_alert=True)
        return
    
    await state.update_data(center_city=city_id, center_city_name=city_name)
    
    await callback.message.edit_text(
        f"Город выбран: {city_name}\n\n"
        "Теперь введи адрес центра:"
    )
    await state.set_state(PartnerRegistrationStates.waiting_for_center_address)
    await callback.answer()
