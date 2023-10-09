from aiogram import Bot, Dispatcher, types
from aiogram import executor
from keyboards import start_keyboard
from settings.config import Config
from status_base import create_base
config = Config()

bot = Bot(config.token)
dp = Dispatcher(bot)
create_base()

@dp.message_handler(commands=['start', 'help'])
async def mail(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,text='helloworld!', reply_markup=start_keyboard())


if __name__ == '__main__':
    executor.start_polling(dp)

