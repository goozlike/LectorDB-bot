import telebot
import config
import os
import time
import random
import utils
from telebot import types
from data_handler import SQLighter

bot = telebot.TeleBot(config.token)
need_login_student = set()
need_login_operator = set()
wait_response_operator = set()
wait_deadline = {}

operator_markup = types.ReplyKeyboardMarkup()
operator_markup.add(types.KeyboardButton(text='/confirm : Подтвердить ближайшие съемки', ))
operator_markup.add(types.KeyboardButton(text='/tmt 4 Расписание ближайших съемок (4 дня)'))
#operator_markup.add(types.KeyboardButton(text='/tmt 7 Расписание ближайших съемок (7 дней)'))
operator_markup.add(types.KeyboardButton(text='/deadline Установить дедлайн'))
operator_markup.add(types.KeyboardButton(text='/abort Сбросить подтверждения'))


stud_markup = types.ReplyKeyboardMarkup()
stud_markup.add(types.KeyboardButton(text='/stmt 4 : Раписание на 4 дня', ))
stud_markup.add(types.KeyboardButton(text='/sdeadl 4 : Дедлайны на 4 дня', ))
stud_markup.add(types.KeyboardButton(text='/stmt 7 : Раписание на 7 дней', ))
stud_markup.add(types.KeyboardButton(text='/sdeadl 7 : Дедлайны на 7 дней', ))



@bot.message_handler(commands=['start'])
def register(message):
    print(message.text)
    chat_id = message.chat.id
    if chat_id in need_login_student:
        need_login_student.remove(chat_id)
    if chat_id in need_login_operator:
        need_login_operator.remove(chat_id)

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='Я студент', callback_data='reg_student')
    button2 = types.InlineKeyboardButton(text='Я оператор', callback_data='reg_operator')
    markup.add(button1)
    markup.add(button2)
    bot.send_message(message.chat.id, '''Здравствуйте!''', reply_markup=types.ReplyKeyboardRemove())
    
    bot.send_message(message.chat.id, '''Зарегестрируйтесь нажав на одну из этих кнопок:''', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    chat_id = call.message.chat.id

    if call.data == 'reg_operator':
        bot.send_message(chat_id, "напишите: Имя Фамилия email \nпример: Иван Васин igorvasin@mail.ru")
        need_login_operator.add(chat_id)

    elif call.data == 'reg_student':
        bot.send_message(chat_id, "напишите: Имя Фамилия группу \nпример: Иван Васин 185")
        need_login_student.add(chat_id)
    
    elif call.data[0] == 'd':
        class_id = call.data.split(' ')[1]
        wait_deadline[call.message.chat.id] = class_id
        bot.send_message(chat_id, "напишите: yyyy-mm-dd hh:mm дедлайн\nпример: 2020-12-20 23:59 дедлайн дз5")

    elif call.data == 'reset_deadl':
        wait_deadline.pop(chat_id, None)
        bot.send_message(chat_id, 'Ok', reply_markup=operator_markup)




#получаем статус клиента
@bot.message_handler(commands=['status'])
def send_status(message):
    status = utils.check_user(message.chat.id)
    bot.send_message(message.chat.id, status)


#REGISTER AS OPERATOR STEP 2
@bot.message_handler(func=lambda message: message.chat.id in need_login_operator)
def chech_login_op(message):
    try:
        data = message.text.split(' ')
        name = data[0]
        lastname = data[1]
        email = data[2]
        if utils.reg_operator(message.chat.id, name, lastname, email):
            bot.send_message(message.chat.id, "Успешно", reply_markup=operator_markup)
            need_login_operator.remove(message.chat.id)
        else:
            bot.send_message(message.chat.id, "Что-то пошло не так. Проверьте еще раз свои данные, если все равно не получается, напишите @goozlike")
    except:
        bot.send_message(message.chat.id, "напишите: Имя Фамилия email \nпример: Иван Васин igorvasin@mail.ru\nчтобы начать все заново напишите /start")


#REGISTER AS STUDENT STEP 2
@bot.message_handler(func=lambda message: message.chat.id in need_login_student)
def chech_login_stud(message):
    try:
        data = message.text.split(' ')
        name = data[0]
        lastname = data[1]
        group = data[2]
        if utils.reg_student(message.chat.id, name, lastname, group):
            bot.send_message(message.chat.id, "Успешно", reply_markup=stud_markup)
            need_login_student.remove(message.chat.id)  
        else:
            bot.send_message(message.chat.id, "Что-то пошло не так. Проверьте еще раз свои данные, если все равно не получается, напишите @goozlike")
    except:
        bot.send_message(message.chat.id, "напишите: Имя Фамилия группу \nпример: Иван Васин 185\nчтобы начать все заново напишите /start")


#подтверждение съемки операторами
@bot.message_handler(commands=['confirm'])
def send_confirm(message):
    status = utils.check_user(message.chat.id) 
    if status == 'op' or status == 's/o':
        query = SQLighter(config.database_name).get_query(message.chat.id)

        if query[0][0] is not None:
            markup = types.ReplyKeyboardMarkup()
            markup.row('Буду снимать')
            markup.row('Не буду снимать')
            bot.send_message(message.chat.id, query[0][1] + '\n' + query[0][2] + '\n' + query[0][3],  reply_markup=markup)
            wait_response_operator.add(message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Похоже, что ничего не запланирвано.', reply_markup=operator_markup)
        
#cброс подтверждений
@bot.message_handler(commands=['abort'])
def abort_confirm(message):
    if message.chat.id in wait_response_operator:
        wait_response_operator.remove(message.chat.id)

    db = SQLighter(config.database_name)
    db.abort_confirm(message.chat.id)
    bot.send_message(message.chat.id, "Успешно",  reply_markup=operator_markup)
    print(db.get_all_queries(message.chat.id, 7))


 
@bot.message_handler(func=lambda message: message.chat.id in wait_response_operator)
def commit_query(message):
    if message.text == 'Буду снимать':
        res = SQLighter(config.database_name).commit(message.chat.id, '1')
        if res:
            query = SQLighter(config.database_name).get_query(message.chat.id)
            if query[0][0] is not None:
                markup = types.ReplyKeyboardMarkup()
                markup.row('Буду снимать')
                markup.row('Не буду снимать')
                bot.send_message(message.chat.id, query[0][1] + '\n' + query[0][2] + '\n' + query[0][3],  reply_markup=markup)
                wait_response_operator.add(message.chat.id)
            else:
                wait_response_operator.remove(message.chat.id)
                bot.send_message(message.chat.id, 'Похоже, что ничего не запланирвано.', reply_markup = operator_markup)

        else:
            wait_response_operator.remove(message.chat.id)
            bot.send_message(message.chat.id, 'Похоже, что ничего не запланирвано.', reply_markup = operator_markup)

    elif message.text == 'Не буду снимать':
        res = SQLighter(config.database_name).commit(message.chat.id, '-1')
        if res:
            query = SQLighter(config.database_name).get_query(message.chat.id)
            if query[0][0] is not None:
                markup = types.ReplyKeyboardMarkup()
                markup.row('Буду снимать')
                markup.row('Не буду снимать')
                bot.send_message(message.chat.id, query[0][1] + '\n' + query[0][2] + '\n' + query[0][3],  reply_markup=markup)
                wait_response_operator.add(message.chat.id)
            else:
                wait_response_operator.remove(message.chat.id)
                bot.send_message(message.chat.id, 'Похоже, что ничего не запланирвано.', reply_markup = operator_markup)
        else:
            wait_response_operator.remove(message.chat.id)
            bot.send_message(message.chat.id, 'Похоже, что ничего не запланирвано.', reply_markup = operator_markup)



#DEADLINES
@bot.message_handler(commands=['deadline'])
def choose_deadl(message):
    db = SQLighter(config.database_name)
    classes = db.get_all_queries(message.chat.id, 7)
    markup = types.InlineKeyboardMarkup()

    for c in classes:
        id_class = c[0]
        text = c[1] + ' ' + c[2] + ' ' + c[3][:-7]
        markup.add(types.InlineKeyboardButton(text=text, callback_data = 'd ' + str(id_class)))

    markup.add(types.InlineKeyboardButton(text='Отмена', callback_data = 'reset_deadl'))

    bot.send_message(message.chat.id, "Выберите занятие, на которое хотите установить дедлайн",reply_markup=markup)

@bot.message_handler(func=lambda message: message.chat.id in wait_deadline)
def set_deadline(message):
    class_id = wait_deadline[message.chat.id]

    db = SQLighter(config.database_name)
    #try:
    date = message.text[:16] + ':00.000'
    text = message.text[16:]
    if db.set_deadline(class_id, message.chat.id, text, time):
        wait_deadline.pop(message.chat.id, None)
        bot.send_message(message.chat.id, "Успешно", reply_markup=operator_markup)
        return
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Отмена', callback_data='reset_deadl'))
        bot.send_message(message.chat.id, "Проверьте правильность или напишите", reply_markup=markup)

    #except:
    #    markup = types.InlineKeyboardMarkup()
    #    markup.add(types.InlineKeyboardButton(text='Отмена', callback_data='reset_deadl'))
    #    bot.send_message(message.chat.id, "Проверьте правильность или напишите", reply_markup=markup)
#
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Отмена', callback_data='reset_deadl'))




#РАСПИСАНИЯ И СПИСКИ ДЕДЛАЙНОВ
#student request to week timetable
@bot.message_handler(commands=['stmt'])
def student_timetable(message):
    try:
        days = message.text.split(' ')[1]
    except:
        bot.send_message(message.chat.id, "bad argument")
        return
    
    db = SQLighter(config.database_name)
    classes = db.stud_tmt(message.chat.id, int(days))
    for c in classes:
        bot.send_message(message.chat.id, c[0] + '\n' + c[1] + '\n' + c[2][:-7])
    
#student request to deadlines
@bot.message_handler(commands=['sdeadl'])
def student_deadlines(message):
    try:
        days = message.text.split(' ')[1]
    except:
        bot.send_message(message.chat.id, "bad argument")
        return

    db = SQLighter(config.database_name)
    deadlines = db.stud_deadl(message.chat.id, int(days))
    if len(deadlines):
        for d in deadlines:
            bot.send_message(message.chat.id, d[0] + '\n' + d[1][:-7] + '\n' + d[2], reply_markup=stud_markup)
    else:
        bot.send_message(message.chat.id, 'Кажется нет активны дедалйнов', reply_markup=stud_markup)


#handle operator request to timetable
@bot.message_handler(commands=['tmt'])
def student_timetable(message):
    try:
        days = message.text.split(' ')[1]
    except:
        bot.send_message(message.chat.id, "bad argument")
        return
    
    db = SQLighter(config.database_name)
    classes = db.get_all_queries(message.chat.id, days)
    for c in classes:
        status = c[4]
        if status == '0' or status == 0:
            status = 'Не подтверждено'
        elif status == '1' or status == 1:
            status = 'Подтверждено'
        elif status == '-1' or status == -1:
            status = 'Отказ'

        bot.send_message(message.chat.id, c[1] + '\n' + c[2] + '\n' + c[3] + '\nСтатус: ' + status)

if __name__ == '__main__':
    bot.polling(none_stop=True)