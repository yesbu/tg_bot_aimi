from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from dishka import FromDishka
from loguru import logger

from src.infrastructure.utils import generate_qr_code


router = Router()

