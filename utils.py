# -*- coding: utf-8 -*-
import shelve
from data_handler import SQLighter
from config import shelve_name, database_name
from random import shuffle


#REGISTER AND USER STATUS THINGS
#get user status
def check_user(chat_id):
    with shelve.open(shelve_name) as storage:
        if str(chat_id) in storage:
            return storage[str(chat_id)]
        
        db = SQLighter(database_name)
        status = db.check(chat_id)
        storage[str(chat_id)] = status
        return status

#set user status
def set_status(chat_id, status):
    with shelve.open(shelve_name) as storage:
        storage[str(chat_id)] = status

#register operator
def reg_operator(chat_id, name, lastname, email):
    db = SQLighter(database_name)
    res = db.register_op(chat_id, name + ' ' + lastname, email)

    with shelve.open(shelve_name) as storage:
        #if registration is done
        print(res)
        if len(res) and res[0][0] == str(chat_id):
            if str(chat_id) in storage:
                old_status = storage[str(chat_id)]
                if old_status == 'stud' or old_status == 's/o':
                    storage[str(chat_id)] = 's/o'
                else:
                    storage[str(chat_id)] = 'op'
                return True
            else:
                storage[str(chat_id)] = 'op'
                return True
        else:
            return False

#register as student
def reg_student(chat_id, name, lastname, group):
    db = SQLighter(database_name)
    res = db.register_stud(chat_id, name + ' ' + lastname, group)
    print(res)
    with shelve.open(shelve_name) as storage:
        if len(res) and res[0][0] == str(chat_id):
            if str(chat_id) in storage:
                old_status = storage[str(chat_id)]
                if old_status == 'op' or old_status == 's/o':
                    storage[str(chat_id)] = 's/o'
                else:
                    storage[str(chat_id)] = 'stud'
                return True
            else:
                storage[str(chat_id)] = 'stud'
                return True
        else:
            return False

def get_rows_count():
    """
    Получает из хранилища количество строк в БД
    :return: (int) Число строк
    """
    with shelve.open(shelve_name) as storage:
        rowsnum = storage['rows_count']
    return rowsnum


def set_user_game(chat_id, estimated_answer):
    """
    Записываем юзера в игроки и запоминаем, что он должен ответить.
    :param chat_id: id юзера
    :param estimated_answer: правильный ответ (из БД)
    """
    with shelve.open(shelve_name) as storage:
        storage[str(chat_id)] = estimated_answer


def finish_user_game(chat_id):
    """
    Заканчиваем игру текущего пользователя и удаляем правильный ответ из хранилища
    :param chat_id: id юзера
    """
    with shelve.open(shelve_name) as storage:
        del storage[str(chat_id)]


def get_answer_for_user(chat_id):
    """
    Получаем правильный ответ для текущего юзера.
    В случае, если человек просто ввёл какие-то символы, не начав игру, возвращаем None
    :param chat_id: id юзера
    :return: (str) Правильный ответ / None
    """
    with shelve.open(shelve_name) as storage:
        try:
            answer = storage[str(chat_id)]
            return answer
        # Если человек не играет, ничего не возвращаем
        except KeyError:
            return None


#def generate_markup(right_answer, wrong_answers):
#    """
#    Создаем кастомную клавиатуру для выбора ответа
#    :param right_answer: Правильный ответ
#    :param wrong_answers: Набор неправильных ответов
#    :return: Объект кастомной клавиатуры
#    """
#    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
#    # Склеиваем правильный ответ с неправильными
#    all_answers = '{},{}'.format(right_answer, wrong_answers)
#    # Создаем лист (массив) и записываем в него все элементы
#    list_items = []
#    for item in all_answers.split(','):
#        list_items.append(item)
#    # Хорошенько перемешаем все элементы
#    shuffle(list_items)
#    # Заполняем разметку перемешанными элементами
#    for item in list_items:
#        markup.add(item)
#    return markup