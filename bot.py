import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, StateFilter
import asyncio

TOKEN = '7697967543:AAGageysIyylm-tOPgBLnsKBveqBR5ePGas'
MANAGER_ID = None  # ID менеджера будет установлен после получения сообщения от менеджера

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)


class OrderCarStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_brand = State()
    waiting_for_model = State()
    waiting_for_year = State()
    waiting_for_custom_year = State()
    waiting_for_budget = State()


@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Заказать автомобиль'))
    keyboard.add(KeyboardButton('Связь через чат'))
    keyboard.add(KeyboardButton('Пример договора'))
    keyboard.add(KeyboardButton('Наше портфолио'))

    await message.answer(
        "Привет! Я бот для заказа автомобилей из Кореи в Россию. Чем могу помочь?",
        reply_markup=keyboard
    )


@dp.message(lambda message: message.text == 'Заказать автомобиль')
async def order_car(message: types.Message, state: FSMContext):
    await message.answer("Как к вам можно обращаться?")
    await state.set_state(OrderCarStates.waiting_for_name)


@dp.message(StateFilter(OrderCarStates.waiting_for_name))
async def enter_name(message: types.Message, state: FSMContext):
    await state.update_data(client_name=message.text)
    # Создаем клавиатуру для выбора марки автомобиля
    brands = ["Hyundai", "Kia", "BMW", "Benz", "Audi", "Toyota", "Chevrolet", "Renault Korea", "Ssangyong", "Другие марки"]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=brand, callback_data=f"brand_{brand.lower()}")] for brand in brands
        ]
    )
    await message.answer("Выберите марку автомобиля:", reply_markup=keyboard)
    await state.set_state(OrderCarStates.waiting_for_brand)


@dp.callback_query(StateFilter(OrderCarStates.waiting_for_brand))
async def select_brand(callback_query: types.CallbackQuery, state: FSMContext):
    brand = callback_query.data.split('_')[1]
    if brand == 'другие марки':
        await callback_query.message.answer("Какая марка автомобиля вас интересует? (Напишите марку)")
        await state.set_state(OrderCarStates.waiting_for_brand)
    else:
        await state.update_data(car_brand=brand)
        # Создаем клавиатуру для выбора модели автомобиля
        models = {
            "hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Palisade"],
            "kia": ["K5", "K3", "K9", "Sportage", "Sorento"],
            "bmw": ["3 Series", "5 Series", "7 Series", "X3", "X5"],
            "benz": ["A-Class", "C-Class", "E-Class", "S-Class", "GLE"],
            "audi": ["A3", "A4", "A6", "Q3", "Q5"],
            "toyota": ["Corolla", "Camry", "RAV4", "Highlander", "Land Cruiser"],
            "chevrolet": ["Spark", "Aveo", "Cruze", "Malibu", "Trax"],
            "renault korea": ["SM3", "SM5", "QM3", "QM5", "QM6"],
            "ssangyong": ["Tivoli", "Korando", "Rexton", "Rodius", "Actyon"]
        }
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=model, callback_data=f"model_{model.lower()}")] for model in models[brand]
            ]
        )
        await callback_query.message.answer("Выберите модель автомобиля:", reply_markup=keyboard)
        await state.set_state(OrderCarStates.waiting_for_model)


@dp.callback_query(StateFilter(OrderCarStates.waiting_for_model))
async def select_model(callback_query: types.CallbackQuery, state: FSMContext):
    model = callback_query.data.split('_')[1]
    await state.update_data(car_model=model)
    # Создаем клавиатуру для выбора года автомобиля
    years = [2019, 2020, 2021, 2022]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=str(year), callback_data=f"year_{year}")] for year in years
        ] + [
            [InlineKeyboardButton(text="Другой год", callback_data="year_other")]
        ]
    )
    await callback_query.message.answer("Выберите год выпуска автомобиля (рекомендуется от 3 до 5 лет):", reply_markup=keyboard)
    await state.set_state(OrderCarStates.waiting_for_year)


@dp.callback_query(StateFilter(OrderCarStates.waiting_for_year))
async def select_year(callback_query: types.CallbackQuery, state: FSMContext):
    year_data = callback_query.data.split('_')[1]
    if year_data == 'other':
        await callback_query.message.answer("Введите год выпуска автомобиля:")
        await state.set_state(OrderCarStates.waiting_for_custom_year)
    else:
        await state.update_data(car_year=year_data)
        await callback_query.message.answer("Какой у вас бюджет?")
        await state.set_state(OrderCarStates.waiting_for_budget)


@dp.message(StateFilter(OrderCarStates.waiting_for_custom_year))
async def enter_custom_year(message: types.Message, state: FSMContext):
    await state.update_data(car_year=message.text)
    await message.answer("Какой у вас бюджет?")
    await state.set_state(OrderCarStates.waiting_for_budget)


@dp.message(StateFilter(OrderCarStates.waiting_for_budget))
async def enter_budget(message: types.Message, state: FSMContext):
    await state.update_data(budget=message.text)
    data = await state.get_data()
    order_details = (
        f"Имя клиента: {data['client_name']}\n"
        f"Марка автомобиля: {data['car_brand']}\n"
        f"Модель автомобиля: {data['car_model']}\n"
        f"Год выпуска: {data['car_year']}\n"
        f"Бюджет: {data['budget']} рублей"
    )
    await message.answer(f"Ваш заказ:\n{order_details}\n\nНаши специалисты скоро с вами свяжутся для уточнения деталей.")

    # Отправка информации менеджеру
    if MANAGER_ID:
        await bot.send_message(MANAGER_ID, f"Новый заказ:\n{order_details}")
    else:
        await message.answer("Ошибка: ID менеджера не установлен. Пожалуйста, попросите менеджера отправить сообщение боту.")
    await state.clear()


@dp.message(lambda message: message.text == 'Связь через чат')
async def contact_support(message: types.Message):
    await message.answer("Переводим вас в чат со специалистом. Пожалуйста, подождите...")


@dp.message(lambda message: message.text == 'Пример договора')
async def example_contract(message: types.Message):
    await message.answer(
        "Вот пример договора:\n\n"
        "1. Обязательства сторон...\n"
        "2. Условия оплаты...\n"
        "3. Сроки доставки...\n"
        "(Пожалуйста, свяжитесь с нами для получения полного текста договора.)"
    )


@dp.message(lambda message: message.text == 'Наше портфолио')
async def portfolio(message: types.Message):
    await message.answer(
        "Наше портфолио доступно по следующей ссылке: [Портфолио компании](http://example.com)"
    )


@dp.message(lambda message: message.from_user.username == 'svetatulya16')
async def set_manager_id(message: types.Message):
    global MANAGER_ID
    MANAGER_ID = message.from_user.id
    await message.answer(f"ID менеджера установлен: {MANAGER_ID}")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

