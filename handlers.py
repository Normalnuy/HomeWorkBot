import config, datetime, asyncio, logging
from aiogram import F, Router, Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from db import UsersDataBase, HomeWorkBase
from states import *
from languages import ru_pack, ua_pack

bot = None 
router = Router()
db = UsersDataBase()
db_work = HomeWorkBase()

messages = {
    "register_message": {},
    "register_sticker": {},
    "change_sub_message": {},
    "link_message": {}
}

idsub_to_string = {
    "eco_law": "Еко. право",
    "crim_law": "Крим. право",
    "crim_proc": "Крим. процес",
    "now_kz": "Нов. КЗ",
    "law_es": "Право ЄС",
    "civ_law": "Цив. право",
    "civ_proc": "Цив. процес",
    "po_prob": "Правові ОП",
}

intweek_to_strweek = {
        1: '(пн)',
        2: '(вт)',
        3: '(ср)',
        4: '(чт)',
        5: '(пт)',
        6: '(сб)',
        7: '(вс)',
    }

intweek_to_strweek_ua = {
    1: '(пн)',
    2: '(вт)',
    3: '(ср)',
    4: '(чт)',
    5: '(пт)',
    6: '(сб)',
    7: '(нд)',
}

change_language = {
    'ru': ru_pack,
    'ua': ua_pack
}

def set_bot(instance: Bot):
    global bot
    bot = instance

def setup_handlers():
    @router.message(Command("start"))
    async def start_handler(msg: Message, state: FSMContext):
        user_id = msg.from_user.id
        
        member = False
        for group in config.allow_groups:
            member = await bot.get_chat_member(chat_id=group, user_id=user_id)
            if 'ChatMember' in str(type(member)) and str(type(member)) != 'ChatMemberLeft':
                member = True
                break
            
        if not member:
            await msg.answer("❌ <b>Ваша группа не подключена к боту!</b>")
            return
                    
        user_username = msg.from_user.username    
        await msg.delete()
        
        if user_id not in messages['register_sticker']:
            messages['register_sticker'][user_id] = {}
        messages['register_sticker'][user_id] = await msg.answer_sticker(config.WELCOME_STICKER)
        
        user = await db.get_user(user_id)
        if not user:    
            await state.set_state(AddNewUser.real_name)
            if user_id not in messages['register_message']:
                messages['register_message'][user_id] = {}
            messages['register_message'][user_id] = await msg.answer(f"👋 <b>Привет, {user_username}!</b>\n\nМеня зовут <b>Sherman</b>, а как мне называть тебя?\n<b>Введи, пожалуйста, своё настоящее имя или фамилию...</b>")
        
        else:
            lang = change_language[user[4]]
            messages['register_message'][user_id] = await msg.answer(lang.welcome.format(user=user[2]), reply_markup=lang.general_menu)


@router.message(Command("help"))
async def help_command(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    await msg.delete()
    
    user = await db.get_user(user_id)
    lang = change_language[user[4]]
    
    text = lang.help_text
    
    await msg.answer(text, reply_markup=lang.close)

@router.message(Command("news"))
async def news_command(msg: Message, state: FSMContext):
    await msg.delete()
    
    global news_message
    news_message = await msg.answer("<b>Текст обновления:</b>")
    await state.set_state(NewState.text)
    
@router.message(NewState.text)
async def send_news(msg: Message, state: FSMContext):
    text = msg.text
    await msg.delete()
    await news_message.edit_text("⚙️ <b>Отправка...</b>")
    
    users = await db.get_all_users()
    for user in users:
        if user[0] == config.ADMIN_ID:
            continue
        await bot.send_message(user[0], text)
    await news_message.edit_text("✅ <b>Отправлено!</b>")

# =================================================== REGISTER ======================================================== #

@router.message(AddNewUser.real_name)
async def get_user_realname(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    
    real_name = msg.text
    message = messages['register_message'][user_id]
    sticker = messages['register_sticker'][user_id]
    
    await sticker.delete()
    await msg.delete()
    await state.update_data(real_name=real_name)
    await state.set_state(AddNewUser.majnor)
    
    text = f"🥰 <b>Приятно познакомиться, {real_name}!</b>\n" \
           f"Перед тобой предметы разных майноров. <b>Жирным</b> я выделил выбранные тобой дисциплины.\n<b>Выбери свой:</b>\n\n" \
           f"🐱 <b>Майнор №1</b>\n" \
           f"<b>1.</b> Екологічне право\n" \
           f"<b>2.</b> Кримінальне право\n" \
           f"<b>3.</b> Кримінальний процес\n" \
           f"<b>4. Новелізація кримінального законодавства</b>\n" \
           f"<b>5.</b> Право Європейського Союзу\n" \
           f"<b>6.</b> Цивільне право\n" \
           f"<b>7.</b> Цивільний процес\n\n" \
           f"🐶 <b>Майнор №2</b>\n" \
           f"<b>1.</b> Екологічне право\n" \
           f"<b>2.</b> Кримінальне право\n" \
           f"<b>3.</b> Кримінальний процес\n" \
           f"<b>4. Правові основи пробації</b>\n" \
           f"<b>5.</b> Право Європейського Союзу\n" \
           f"<b>6.</b> Цивільне право\n" \
           f"<b>7.</b> Цивільний процес\n\n" \
           
    await message.edit_text(text=text, reply_markup=ua_pack.change_majnor)
    
    
@router.callback_query(F.data == 'first_majnor')
@router.callback_query(F.data == 'second_majnor')
async def get_user_majnor(clbck: CallbackQuery, state: FSMContext):
    user_id = clbck.from_user.id
    message = messages['register_message'][user_id]
    
    set_majnor = {
        "first_majnor": 1,
        "second_majnor": 2
    }
    majnor = set_majnor[clbck.data]
    
    await state.update_data(majnor=majnor)
    
    language_btn = [
        [
            InlineKeyboardButton(text="Українська 🇺🇦", callback_data="ua_pack_btn"),
            InlineKeyboardButton(text="Какое-то говно 💩", callback_data="ru_pack_btn")
        ]
    ]
    language = InlineKeyboardMarkup(inline_keyboard=language_btn)
    await message.edit_text("🏁 <b>Выберите язык общения:</b>", reply_markup=language)

@router.callback_query(F.data == 'ua_pack_btn')
@router.callback_query(F.data == 'ru_pack_btn')
async def register_user(clbck: CallbackQuery, state: FSMContext):
    user_id = clbck.from_user.id
    message = messages['register_message'][user_id]
    state_data = await state.get_data()
    await state.clear()
    
    language = clbck.data[0] + clbck.data[1]
    
    await db.add_user(user_id, clbck.from_user.username, state_data['real_name'], state_data['majnor'], language)
    user = await db.get_user(user_id)
    
    lang = change_language[user[4]]
    text = lang.register
    
    await message.delete()
    await clbck.message.answer(text=text, reply_markup=lang.general_menu)
    
# =================================================== ADD HOMEWORK ==================================================== #

@router.message(F.text.lower() == '✍️ добавить')
@router.message(F.text.lower() == '✍️ додати')
async def get_sub_to_add(msg: Message, state: FSMContext):
    await msg.delete()
    user_id = msg.from_user.id
    
    user = await db.get_user(user_id)
    majnor = user[3]
    subs = get_subs_by_majnor(majnor, 'add')
    lang = change_language[user[4]]
    
    if user_id not in messages['change_sub_message']:
        messages['change_sub_message'][user_id] = {}
    messages['change_sub_message'][user_id] = await msg.answer(lang.add_homework, reply_markup=subs)


@router.callback_query(F.data == 'eco_law_add')
@router.callback_query(F.data == 'crim_law_add')
@router.callback_query(F.data == 'crim_proc_add')
@router.callback_query(F.data == 'now_kz_add')
@router.callback_query(F.data == 'law_es_add')
@router.callback_query(F.data == 'civ_law_add')
@router.callback_query(F.data == 'civ_proc_add')
@router.callback_query(F.data == 'po_prob_add')
async def get_homework_info(clbck: CallbackQuery, state: FSMContext):
    user_id = clbck.from_user.id
    user = await db.get_user(user_id)
    lang = change_language[user[4]]
    message = messages['change_sub_message'][user_id]
    
    await state.set_state(AddHomeWork.homework_sub)
    await state.update_data(homework_sub=clbck.data)
    
    await state.set_state(AddHomeWork.homework_text)
    await message.edit_text(lang.input_homework, reply_markup=lang.cancel)
    
@router.message(AddHomeWork.homework_text)
async def get_homework_text(msg: Message, state: FSMContext, error=None):
    user_id = msg.from_user.id
    user = await db.get_user(user_id)
    lang = change_language[user[4]]
    message = messages['change_sub_message'][user_id]
    
    if not error:
        homework_text = msg.text
        
        await msg.delete()
        await state.update_data(homework_text=homework_text)
    
    await message.edit_text(lang.input_time_homework, reply_markup=lang.next_week)
    await state.set_state(AddHomeWork.homework_data)
    
@router.message(AddHomeWork.homework_data)
async def get_homework_data(msg: Message, state: FSMContext, next_data=None):
    user_id = msg.from_user.id
    
    if next_data:
        msg = msg.message
    else:
        await msg.delete()
        
    user = await db.get_user(user_id)
    lang = change_language[user[4]]
    message = messages['change_sub_message'][user_id]
    
    if next_data:
        await state.set_state(AddHomeWork.homework_data)
        await state.update_data(homework_data=next_data)
    else:
        await state.update_data(homework_data=msg.text)
    state_data = await state.get_data()
    
    homework_data = state_data['homework_data']
    
    if homework_data.count(".") != 2:
        await msg.delete()
        await message.edit_text(lang.error_format_time)
        await asyncio.sleep(3)
        await get_homework_text(msg, state, True)
        return
    
    await state.clear()
    part_sub = state_data['homework_sub'].split("_")
    homework_sub = f"{part_sub[0]}_{part_sub[1]}"
    homework_text = state_data['homework_text']
    user_add = user[2]
    full_sub = idsub_to_string[homework_sub]
    
    this_sub = await db_work.get_work(homework_sub, homework_data, user_add)
    if this_sub:
        edit_close_btn = [[InlineKeyboardButton(text=lang.edit_btn_text, callback_data=f"{homework_sub}_edit"), InlineKeyboardButton(text=lang.close_btn_text, callback_data="cancel_close_btn")]]
        edit_close = InlineKeyboardMarkup(inline_keyboard=edit_close_btn)
        await message.edit_text(text=lang.this_sub_error.format(full_sub=full_sub, text=this_sub[2], data=this_sub[3]), reply_markup=edit_close)
        return
    
    await db_work.add_work(homework_sub, homework_text, homework_data, user_add)
    
    datetime_data = datetime.datetime.strptime(homework_data, '%d.%m.%Y')
    homework_week = datetime.datetime.isoweekday(datetime_data)
    
    strweek = intweek_to_strweek[homework_week] if lang == ru_pack else intweek_to_strweek_ua[homework_week]
    
    text = lang.done_add_homework.format(full_sub=full_sub, homework_text=homework_text, homework_data=homework_data, strweek=strweek)
    
    await message.edit_text(text=text, reply_markup=lang.close)
    
# =================================================== DELETE HOMEWORK ================================================= #

@router.message(F.text.lower() == '🗑 удалить')
@router.message(F.text.lower() == '🗑 видалити')
async def get_sub_to_delete(msg: Message, state: FSMContext):
    await msg.delete()

    user_id = msg.from_user.id
    user = await db.get_user(user_id)
    lang = change_language[user[4]]
    majnor = user[3]
    subs = get_subs_by_majnor(majnor, 'dell')

    if user_id not in messages['change_sub_message']:
        messages['change_sub_message'][user_id] = {}
    messages['change_sub_message'][user_id] = await msg.answer(lang.delete_homework, reply_markup=subs)


@router.callback_query(F.data == 'eco_law_dell')
@router.callback_query(F.data == 'crim_law_dell')
@router.callback_query(F.data == 'crim_proc_dell')
@router.callback_query(F.data == 'now_kz_dell')
@router.callback_query(F.data == 'law_es_dell')
@router.callback_query(F.data == 'civ_law_dell')
@router.callback_query(F.data == 'civ_proc_dell')
@router.callback_query(F.data == 'po_prob_dell')
async def delete_last_homework(clbck: CallbackQuery, state: FSMContext):
    user_id = clbck.from_user.id
    user = await db.get_user(user_id)
    lang = change_language[user[4]]
    message = messages['change_sub_message'][user_id]

    sub_dell = clbck.data
    part_sub = sub_dell.split("_")
    sub = f"{part_sub[0]}_{part_sub[1]}"
    full_sub = idsub_to_string[sub]

    subs = await db_work.get_all_subs_by_name(sub)

    try:

        sub_db = subs[-1]
        sub_data = sub_db[3]

        homework_text = sub_db[2]
        homework_data = sub_db[3]
        datatime_data = datetime.datetime.strptime(homework_data, "%d.%m.%Y")
        strweek = intweek_to_strweek[datetime.datetime.isoweekday(datatime_data)] if lang == ru_pack else intweek_to_strweek_ua[datetime.datetime.isoweekday(datatime_data)]
        await db_work.dell_work(sub, sub_data)

        text = lang.done_delete_homework.format(full_sub=full_sub, homework_text=homework_text, homework_data=homework_data, strweek=strweek)

        await message.edit_text(text, reply_markup=lang.close)

    except IndexError:
        await message.edit_text(lang.no_found_homework.format(full_sub=full_sub))
    except Exception as e:
        await message.edit_text(lang.unknown_error)
        await bot.send_message(config.ADMIN_ID, text=f"❗️ <b> Неизвестная ошибка от {user[1]}</b>\n<b>Действие:</b> удаление домашнего по \"{full_sub}\"\n<b>Код ошибки:</b> {e}")
        
# =================================================== EDIT HOMEWORK =================================================== #

@router.message(F.text.lower() == '📝 редактировать')
@router.message(F.text.lower() == '📝 редагувати')
async def get_sub_to_edit(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    await msg.delete()

    user = await db.get_user(user_id)
    lang = change_language[user[4]]
    majnor = user[3]
    subs = get_subs_by_majnor(majnor, 'edit')

    if user_id not in messages['change_sub_message']:
        messages['change_sub_message'][user_id] = {}
    messages['change_sub_message'][user_id] = await msg.answer(lang.edit_homework, reply_markup=subs)


@router.callback_query(F.data == 'eco_law_edit')
@router.callback_query(F.data == 'crim_law_edit')
@router.callback_query(F.data == 'crim_proc_edit')
@router.callback_query(F.data == 'now_kz_edit')
@router.callback_query(F.data == 'law_es_edit')
@router.callback_query(F.data == 'civ_law_edit')
@router.callback_query(F.data == 'civ_proc_edit')
@router.callback_query(F.data == 'po_prob_edit')
async def get_edit_text(clbck: CallbackQuery, state: FSMContext):
    user_id = clbck.from_user.id
    user = await db.get_user(user_id)
    lang = change_language[user[4]]
    message = messages['change_sub_message'][user_id]

    part_sub = clbck.data.split('_')
    sub_id = f"{part_sub[0]}_{part_sub[1]}"
    full_sub = idsub_to_string[sub_id]

    await state.set_state(EditHomeWork.edit_sub)
    await state.update_data(edit_sub=sub_id)

    await state.set_state(EditHomeWork.edit_text)
    await message.edit_text(lang.input_edit_homework.format(full_sub=full_sub))


@router.message(EditHomeWork.edit_text)
async def edit_homework_text(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    user = await db.get_user(user_id)
    lang = change_language[user[4]]
    message = messages['change_sub_message'][user_id]

    await state.update_data(edit_text=msg.text)
    state_data = await state.get_data()
    await state.clear()
    await msg.delete()

    full_sub = idsub_to_string[state_data['edit_sub']]


    try:
        subs = await db_work.get_all_subs_by_name(state_data['edit_sub'])
        subs.reverse()
        for sub_db in subs:
            real_name = user[2]
            user_add = sub_db[4]
            if user_add == real_name:

                sub_id = sub_db[1]
                homework_text = state_data['edit_text']
                homework_data = sub_db[3]

                await db_work.update_text(sub_id, homework_text, homework_data)

                datatime_data = datetime.datetime.strptime(homework_data, "%d.%m.%Y")
                strweek = intweek_to_strweek[datetime.datetime.isoweekday(datatime_data)] if lang == ru_pack else intweek_to_strweek_ua[datetime.datetime.isoweekday(datatime_data)]

                text = lang.done_edit_homework.format(full_sub=full_sub, homework_text=homework_text, homework_data=homework_data, strweek=strweek)
                await message.edit_text(text, reply_markup=lang.close)
                return

        await message.edit_text(lang.no_found_homework.format(full_sub=full_sub))

    except IndexError:
        await message.edit_text(lang.no_found_homework.format(full_sub=full_sub))
    except Exception as e:
        await message.edit_text(lang.unknown_error)
        await bot.send_message(config.ADMIN_ID, text=f"❗️ <b> Неизвестная ошибка от {user[1]}</b>\n<b>Действие:</b> редактирование домашнего по \"{full_sub}\"\n<b>Код ошибки:</b> {e}")

# =================================================== YESTERDAY HOMEWORK ============================================== #

@router.message(F.text.lower() == '🙇‍♂️ на завтра')
async def yesterday_homework(msg: Message, state: FSMContext):
    await msg.delete()
    user_id = msg.from_user.id
    
    user = await db.get_user(user_id)
    lang = change_language[user[4]]
    homeworks = await db_work.get_all_works()
    
    datetime_yesterday_data = datetime.datetime.now() + datetime.timedelta(days=1)
    yesterday_data = datetime.datetime.strftime(datetime_yesterday_data, "%d.%m.%Y")
    strweek = intweek_to_strweek[datetime.datetime.isoweekday(datetime_yesterday_data)]
    
    subs_and_text = {}
    
    majnor = user[3]
    majnor_subs = {
        1: config.first_majnor_subs,
        2: config.second_majnor_subs
    }
    my_subs = majnor_subs[majnor]
    
    user_homeworks = lang.yesterday_general.format(yesterday_data=yesterday_data, strweek=strweek)
    for homework in homeworks:
        sub = homework[1]
        homework_text = homework[2]
        homework_data = homework[3]
        user_add = homework[4]
        real_name = user[2]
        
        if yesterday_data == homework_data:
            if sub in my_subs:
                if real_name == user_add:
                    
                    if sub not in subs_and_text:
                        subs_and_text[sub] = {"homework_text": ''}
                        
                    if subs_and_text[sub]["homework_text"] != '':
                        subs_and_text[sub]["homework_text"] = ''
                    
                    if subs_and_text[sub]["homework_text"] == '':
                        subs_and_text[sub]["homework_text"] += f"{homework_text}"

                else:
                    
                    if sub not in subs_and_text:
                        subs_and_text[sub] = {"homework_text": ''}
                    
                    if subs_and_text[sub]["homework_text"] == '':
                        subs_and_text[sub]["homework_text"] += f"{homework_text} || {user_add}"

    
    if not subs_and_text:
        user_homeworks = lang.yesterday_no_found
    else:
        status = False
        for key, value in subs_and_text.items():
            value = value['homework_text']
            if '||' in value:
                status = True
            user_homeworks += f"<b>{idsub_to_string[key]}</b>: {value}\n"
            
        if status:
            user_homeworks += lang.other_student_symbol
    
    await msg.answer(text=user_homeworks, reply_markup=lang.close)

# =================================================== WEEK HOMEWORK =================================================== #

@router.message(F.text.lower() == 'текущая неделя')
@router.message(F.text.lower() == 'следующая неделя')
@router.message(F.text.lower() == 'цей тиждень')
@router.message(F.text.lower() == 'наступний тиждень')
async def week_homework(msg: Message, state: FSMContext):
    
    change_status = {
        "текущая неделя": 0,
        "цей тиждень": 0,
        "следующая неделя": 7,
        "наступний тиждень": 7
    }
    status = change_status[msg.text.lower()]
    await msg.delete()
    
    user_id = msg.from_user.id
    
    user = await db.get_user(user_id)
    lang = change_language[user[4]]
    homeworks = await db_work.get_all_works()
    
    datetime_now_data = datetime.datetime.now() + datetime.timedelta(days=status)
    intweek = datetime.datetime.isoweekday(datetime_now_data)
    dates_list = []
    
    monday = datetime_now_data + datetime.timedelta(days=(intweek * -1) + 1)
    for i in range(0, 7):
        datatime_data = monday + datetime.timedelta(days=i)
        data = datetime.datetime.strftime(datatime_data, '%d.%m.%Y')
        dates_list.append(data)
    
    data_sub_text_dict = {}
    
    majnor = user[3]
    majnor_subs = {
        1: config.first_majnor_subs,
        2: config.second_majnor_subs
    }
    my_subs = majnor_subs[majnor]
    
    for data in dates_list:
        for homework in homeworks:
            
            sub = homework[1]
            homework_text = homework[2]
            homework_data = homework[3]
            user_add = homework[4]
            real_name = user[2]
            
            if data not in data_sub_text_dict:
                data_sub_text_dict[data] = {}
                
            if data == homework_data:
                if sub in my_subs:
                    data_sub_text_dict[data][sub] = ''
                    
                    if real_name == user_add:
                        data_sub_text_dict[data][sub] = homework_text
                    else:
                        if data_sub_text_dict[data][sub] == '':
                            data_sub_text_dict[data][sub] = f"{homework_text} || {user_add}"
    
    user_homeworks = lang.homework_period.format(first_day=dates_list[0], last_day=dates_list[-1])

    status = False
    for data, subs in data_sub_text_dict.items():
        
        datetime_data = datetime.datetime.strptime(data, '%d.%m.%Y')
        strweek = intweek_to_strweek[datetime.datetime.isoweekday(datetime_data)] if lang == ru_pack else intweek_to_strweek_ua[datetime.datetime.isoweekday(datetime_data)]
        
        if not subs:
            user_homeworks += f"\n📍 <b>{data} {strweek}:</b>\n- Пусто 💤\n"
        else:
            user_homeworks += f"\n📍 <b>{data} {strweek}:</b>\n"
            for sub, text in subs.items():
                if '||' in text:
                    status = True
                user_homeworks += f"<b>- {idsub_to_string[sub]}:</b> {text}\n"
                        
    if status:
        user_homeworks += lang.other_student_symbol

    if not data_sub_text_dict:
        user_homeworks = lang.no_week_homework
    
    await msg.answer(text=user_homeworks, reply_markup=lang.close)

# =================================================== LINKS =========================================================== #

@router.message(F.text.lower() == '🔗 ссылки')
@router.message(F.text.lower() == '🔗 посилання')
async def get_sub_format(msg: Message, state: FSMContext):
    await msg.delete()
    user_id = msg.from_user.id
    user = await db.get_user(user_id)
    lang = change_language[user[4]]
    
    if user_id not in messages['link_message']:
        messages['link_message'][user_id] = {}
        
    messages['link_message'][user_id] = await msg.answer(lang.change_link_format, reply_markup=lang.change_link_format_btns)


@router.callback_query(F.data == 'lecture_btn')
@router.callback_query(F.data == 'practice_btn')
async def get_subs_to_link(clbck: CallbackQuery, state: FSMContext):
    user_id = clbck.from_user.id
    message = messages['link_message'][user_id]
    user = await db.get_user(user_id)
    majnor = user[3]
    lang = change_language[user[4]]
    
    formats = clbck.data.split("_")
    format = formats[0]
    
    subs = get_subs_by_majnor(majnor, f'link_{format}')
    
    await message.edit_text(lang.change_link_sub, reply_markup=subs)

@router.callback_query(lambda c: c.data.startswith('eco_law_link'))
@router.callback_query(lambda c: c.data.startswith('crim_law_link'))
@router.callback_query(lambda c: c.data.startswith('crim_proc_link'))
@router.callback_query(lambda c: c.data.startswith('now_kz_link'))
@router.callback_query(lambda c: c.data.startswith('law_es_link'))
@router.callback_query(lambda c: c.data.startswith('civ_law_link'))
@router.callback_query(lambda c: c.data.startswith('civ_proc_link'))
@router.callback_query(lambda c: c.data.startswith('po_prob_link'))
async def send_link_of_sub(clbck: CallbackQuery, state: FSMContext):
    user_id = clbck.from_user.id
    user = await db.get_user(user_id)
    message = messages['link_message'][user_id]
    lang = change_language[user[4]]
    
    
    clbck_data = clbck.data.split("_")
    sub_id = clbck_data[0] + '_' + clbck_data[1]
    sub_name = idsub_to_string[sub_id]
    format = clbck_data[-1]
    
    
    change_link = {
        "lecture": {
                        "eco_law": 'https://us04web.zoom.us/j/71943425633 cPe1A0',
                        "crim_law": 'https://us04web.zoom.us/j/79113198986?pwd=OW9ZSHRXcG0wSXdwQWZIUXFCRWlUUT09',
                        "crim_proc": 'Отсутствует на АСУ',
                        "now_kz": 'https://us02web.zoom.us/j/82429044522?pwd=UEJDT1ZlYmpGazFZSWJJRk5RVGZsQT09',
                        "law_es": 'https://us04web.zoom.us/j/3021971875?pwd=RTFXMHFhT3R6Q3EyWjlyalFiTmNiQT09&omn=78388754207',
                        "civ_law": 'https://meet.google.com/phx-zqng-qgw',
                        "civ_proc": 'Отсутствует на АСУ',
                        "po_prob": 'https://us05web.zoom.us/j/84872851749?pwd=qH8leLYi0kFpaligy4i1Mu3ih0VDan.1',
                    },
        "practice": {
                        "eco_law": 'https://us04web.zoom.us/j/3527127215?pwd=SFNmQUIvT0tRaHlDaVYrN3l5bzJVQT09',
                        "crim_law": 'https://us04web.zoom.us/j/71664682187?pwd=W8UKnJ1vtU13h8Nb3Ql4ipDkhIMapV.1',
                        "crim_proc": 'https://us05web.zoom.us/j/9670764488?pwd=OEY5NFZvOGljdWVNN0tLQkRPTDVTQT09&omn=89411604995',
                        "now_kz": 'https://us04web.zoom.us/j/71664682187?pwd=W8UKnJ1vtU13h8Nb3Ql4ipDkhIMapV.1',
                        "law_es": 'https://us04web.zoom.us/j/87395265592 3Dyqu4',
                        "civ_law": 'https://us02web.zoom.us/j/8120752981?pwd=RWFTUHhBbWhWKy92SXpiSkFoazlCZz09',
                        "civ_proc": 'https://us02web.zoom.us/j/5567500898 yW6RJc',
                        "po_prob": 'https://us05web.zoom.us/j/84872851749?pwd=qH8leLYi0kFpaligy4i1Mu3ih0VDan.1',
                    }
    }
    link = change_link[format][sub_id]
    
    await message.edit_text(text=lang.get_link_of_sub.format(sub_name=sub_name, format=format, link=link), reply_markup=lang.close)
    
    

# =================================================== BUTTONS ========================================================= #  ======================================================================================================= #
##
##
# =================================================== NEXT WEEK ======================================================= #

@router.callback_query(F.data == 'next_week_btn')
async def next_data_callback(clbck: CallbackQuery, state: FSMContext):
    now = datetime.datetime.now() + datetime.timedelta(days=7)
    str_now = datetime.datetime.strftime(now, '%d.%m.%Y')
    await get_homework_data(clbck, state, str_now)

# =================================================== CANCEL / CLOSE ================================================== #

@router.callback_query(F.data == 'cancel_close_btn')
async def cancel_close_callback(clbck: CallbackQuery, state: FSMContext):
    await state.clear()
    await clbck.message.delete()

# ===================================================================================================================== #

###############       #####          #####       ##########     #####           #####################   
###############       #####          #####       #####  #####   #####         ######################
#####                 #####          #####       #####    ##### #####       #####
#####                 #####          #####       #####      #########       #####
###############       #####          #####       #####        #######       #####
###############       #####          #####       #####          #####       #####  
####                  #####          #####       #####          #####       ##### 
####                  #####          #####       #####          #####       #####
####                  #####          #####       #####          #####       #####
####                   #####        #####        #####          #####         #####################
####                      ############           #####          #####          #####################

# =============================================== FUNCTIONS =========================================================== #

def get_subs_by_majnor(majnor: int, reason: str):
    
    """
    Генерирует кнопки дисциплин.
    
    Аргументы:
    majnor: Майнор студента.
    reason: Причина генерации.
    
    Возвращает: Кнопки дисциплин.
    """
    
    inline_keyboard = []
    current_row = []
    buttons_per_row = 3
    
    what_subs = {
        1: config.first_majnor_subs,
        2: config.second_majnor_subs
    }
    subs = what_subs[majnor]

    for sub in subs:
    
        button_name = idsub_to_string[sub]
        button_callback_data = f"{sub}_{reason}"
        current_row.append(InlineKeyboardButton(text=button_name, callback_data=button_callback_data))
    
        if len(current_row) == buttons_per_row:
            inline_keyboard.append(current_row)
            current_row = []

    current_row.append(InlineKeyboardButton(text="Отменить", callback_data="cancel_close_btn"))
    if current_row:
        inline_keyboard.append(current_row)
    
    
    subs_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return subs_buttons
