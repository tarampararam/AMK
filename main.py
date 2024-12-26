
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from telegram import ReplyKeyboardMarkup

# Токен вашего бота

TOKEN = '7697967543:AAGageysIyylm-tOPgBLnsKBveqBR5ePGas'
# Шаги для ConversationHandler
SELECT_CAR, ENTER_YEAR, ENTER_BUDGET = range(3)

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Стартовая команда
async def start(update: Update, context: CallbackContext):
    # Создаем клавиатуру с кнопками
    keyboard = [
        ['Заказать автомобиль', 'Связь через чат'],
        ['Пример договора', 'Наше портфолио']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    # Приветственное сообщение и кнопки
    await update.message.reply_text('Привет! Я бот для заказа автомобилей из Кореи в Россию. Чем могу помочь?', reply_markup=reply_markup)

# Функция для начала заказа автомобиля
async def order_car(update: Update, context: CallbackContext):
    # Запрашиваем марку, год и бюджет автомобиля
    await update.message.reply_text(
        "Какая марка автомобиля вас интересует? (Напишите марку)"
    )
    return SELECT_CAR

# Шаг 1: Выбор марки автомобиля
async def select_car(update: Update, context: CallbackContext):
    context.user_data['car_brand'] = update.message.text  # Сохраняем марку автомобиля
    await update.message.reply_text(
        "Какой год выпуска вас интересует? (Возраст автомобиля от 3 до 5 лет)"
    )
    return ENTER_YEAR

# Шаг 2: Ввод года выпуска
async def enter_year(update: Update, context: CallbackContext):
    year = int(update.message.text)
    if 3 <= year <= 5:
        context.user_data['car_year'] = year  # Сохраняем год выпуска
        await update.message.reply_text("Какой у вас бюджет?")
        return ENTER_BUDGET
    else:
        await update.message.reply_text("Год выпуска должен быть от 3 до 5 лет. Пожалуйста, укажите правильный год.")
        return ENTER_YEAR

# Шаг 3: Ввод бюджета
async def enter_budget(update: Update, context: CallbackContext):
    context.user_data['budget'] = update.message.text  # Сохраняем бюджет
    car_brand = context.user_data['car_brand']
    car_year = context.user_data['car_year']
    budget = context.user_data['budget']

    # Подтверждаем заказ
    await update.message.reply_text(
        f"Вы заказали автомобиль:\n\nМарка: {car_brand}\nГод выпуска: {car_year} года\nБюджет: {budget} рублей\n\n"
        "Наши специалисты скоро с вами свяжутся для уточнения деталей."
    )

    return ConversationHandler.END

# Функция для связи через чат
async def contact_support(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Переводим вас в чат со специалистом. Пожалуйста, подождите..."
    )
    # Пример отправки сообщения специалисту
    # (Вы можете заменить этот шаг на реальную интеграцию с CRM или чат-системой)
    await update.message.reply_text("Скоро с вами свяжется наш специалист!")

# Функция для примера договора
async def example_contract(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Вот пример договора:\n\n"
        "1. Обязательства сторон...\n"
        "2. Условия оплаты...\n"
        "3. Сроки доставки...\n"
        "(Пожалуйста, свяжитесь с нами для получения полного текста договора.)"
    )

# Функция для отображения портфолио
async def portfolio(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Наше портфолио доступно по следующей ссылке: [Портфолио компании](http://example.com)"
    )

# Главная функция для запуска
async def main():
    # Инициализация приложения
    application = Application.builder().token(TOKEN).build()

    # ConversationHandler для заказа автомобиля
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, order_car)],

        states={
            SELECT_CAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_car)],
            ENTER_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_year)],
            ENTER_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_budget)],
        },

        fallbacks=[],
    )

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.Regex('^Связь через чат$'), contact_support))
    application.add_handler(MessageHandler(filters.Regex('^Пример договора$'), example_contract))
    application.add_handler(MessageHandler(filters.Regex('^Наше портфолио$'), portfolio))

    # Запуск бота с использованием встроенной обработки событий
    await application.run_polling()

if __name__ == '__main__':
    import asyncio

    # Убираем блокировку цикла событий и запускаем бота с asyncio
    asyncio.run(main())

