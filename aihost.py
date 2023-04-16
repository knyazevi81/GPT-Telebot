import sqlite3
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import openai
import config

connect = sqlite3.connect('telegram_base.bd')
cursor = connect.cursor()

openai.api_key = config.ai_token
model_engine = 'text-davinci-003'
max_tokens = 128


bot = Bot(config.tele_token)
dp = Dispatcher(bot)

menu_button = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/menu'))


@dp.message_handler(commands=['start', 'menu'])
async def questions(message: types.Message):

    all_reg_id = cursor.execute('SELECT profile_id FROM all_profiles').fetchall()

    if (message.from_user.id,) in all_reg_id and message.chat.type == 'private':
        activity_profile = cursor.execute(f'SELECT activity, super_user FROM all_profiles WHERE profile_id == {message.from_user.id}').fetchall()
        true_activity = ''
        admin_panel = ''
        request_for = ''
        if activity_profile[0][0] == 'false' or activity_profile == []:
            true_activity = '⛔ нет доступа'
            request_for = 'Чтобы получить доступ к боту, введите идентификационный ключ!'
        else:
            true_activity = '✅ доступ разрешен'
            request_for = 'Можете вводить свой запрос'

        if activity_profile[0][1] == 'false' or activity_profile == []:
            admin_panel = '⛔ нет доступа'
        else:
            admin_panel = '✅ доступ разрешен'

        await bot.send_message(message.from_user.id, '👀 Приветствую! это ChatGPT-3 бот\n'
                                                     '----------------------------------\n'
                                                     f'Статус доступа: {true_activity}\n'
                                                     f'Режим Администратора: {admin_panel}\n'
                                                     f'---------------------------------\n'
                                                     f'{request_for}\n'
                                                     f'---------------------------------\n'
                                                     '👥 проект находится на стадии разработки в случае проблем'
                                                     ' и покупке ключей, писать @ilpdakz')
    else:
        await bot.send_message(message.from_user.id, '✅ Вы вы успешно зарегистрировались в базе данных\n'
                                                     'Нажмите еще раз /menu чтобы увидеть меню профиля',
                               reply_markup=menu_button)
        data = (int(message.from_user.id), 'false', 'false')
        cursor.execute('INSERT INTO all_profiles(profile_id, activity, super_user) VALUES(?,?,?)', data)
        connect.commit()
        print(message.from_user.id)


@dp.message_handler()
async def questions(message: types.Message):
    if message.text[0:3] == 'tok' and message.chat.type == 'private':
        token = message.text.split()[0]
        nice_tokens = cursor.execute(f"SELECT activity FROM all_tokens WHERE token_num = '{token}'").fetchall()
        if nice_tokens[0][0] == 'false':
            cursor.execute(f"UPDATE all_tokens SET activity = ? WHERE token_num = '{token}'", ('true',))
            cursor.execute(f"UPDATE all_profiles SET activity = ? WHERE profile_id = '{message.from_user.id}'", ('true',))
            await bot.send_message(message.from_user.id, '✅ Вы успешно активировали ключ!', reply_markup=menu_button)
        else:
            await bot.send_message(message.from_user.id, '⛔ Данный ключ уже используется!', reply_markup=menu_button)
        connect.commit()

    elif message.text.split()[0].lower() == 'admin' and message.text.split()[1] == config.admin_pass:
        cursor.execute(f"UPDATE all_profiles SET super_user = ? WHERE profile_id = '{message.from_user.id}'", ('true',))
        await bot.send_message(message.from_user.id, '✅ Вы успешно активировали режим администратора', reply_markup=menu_button)
        connect.commit()

    elif message.text.split()[0].lower() == 'admin' and message.text.split()[1].lower() == 'users':
        true_admin = cursor.execute(f"SELECT super_user FROM all_profiles WHERE profile_id = '{message.from_user.id}'").fetchone()
        if true_admin[0] == 'true':
            all_data = '----------(all_users)----------\n id_profile|activity|super_user\n'
            list_users = cursor.execute('SELECT profile_id, activity, super_user FROM all_profiles').fetchall()
            for i in range(len(list_users)):
                all_data += f'{list_users[i][0]} | {list_users[i][1]} | {list_users[i][2]}\n'
            await bot.send_message(message.from_user.id, all_data)
        else:
            await bot.send_message(message.from_user.id, '⛔ у вас не доступа')

    elif message.text.split()[0].lower() == 'admin' and message.text.split()[1].lower() == 'tokens':
        true_admin = cursor.execute(f"SELECT super_user FROM all_profiles WHERE profile_id = '{message.from_user.id}'").fetchone()
        if true_admin[0] == 'true':
            list_tokens = cursor.execute('SELECT token_num, activity FROM all_tokens').fetchall()
            all_data = '----------(all_users)----------\n    token  |  activity  \n'
            for i in range(len(list_tokens)):
                all_data += f"{list_tokens[i][0]}|{list_tokens[i][1]}\n"
            await bot.send_message(message.from_user.id, all_data)
        else:
            await bot.send_message(message.from_user.id, '⛔ у вас не доступа')

    elif message.text.split()[0].lower() == 'admin' and message.text.split()[1].lower() == 'updb':
        true_admin = cursor.execute(f"SELECT super_user FROM all_profiles WHERE profile_id = '{message.from_user.id}'").fetchone()
        if true_admin[0] == 'true':
            input_data = cursor.execute(message.text[11:len(message.text)]).fetchall()
            await bot.send_message(message.from_user.id, input_data)
        else:
            await bot.send_message(message.from_user.id, '⛔ у вас не доступа')


    else:
        user_activity = cursor.execute(f"SELECT activity FROM all_profiles WHERE profile_id = '{message.from_user.id}'").fetchone()
        if user_activity[0] == 'true':
            completion = openai.Completion.create(
                engine=model_engine,
                prompt=message.text,
                max_tokens=500,
                temperature=0.5,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            await bot.send_message(message.from_user.id, completion.choices[0].text)
        else:
            await bot.send_message(message.from_user.id, '⛔ У вас нет доступа', reply_markup=menu_button)


if __name__ == '__main__':
    executor.start_polling(dp)
    connect.close()
