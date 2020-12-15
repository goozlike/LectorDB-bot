# -*- coding: utf-8 -*-
import sqlite3

class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    #получить завтрашние занятия
    #'all' - все
    #'bad' - неподтвержденные или подтвержденный отказ
    def get_tmr_classes(self, flag='all'):
        if flag=='bad':
            with self.connection:

                # return self.cursor.execute('SELECT * FROM Classes_Groups WHERE start_time > date("2020-12-20", "+1 day") AND start_time < date("2020-12-20", "+2 day")')
                return self.cursor.execute('''
                    SELECT * FROM Classes_Groups
                    JOIN Classes ON Classes.id_class = Classes_Groups.id_class
                    WHERE start_time > date("2020-12-20", "+1 day")
                    AND start_time < date("2020-12-20", "+2 day")
                    AND confirmed < 1
                ''').fetchall()
        elif flag=='all':
            with self.connection:

                # return self.cursor.execute('SELECT * FROM Classes_Groups WHERE start_time > date("2020-12-20", "+1 day") AND start_time < date("2020-12-20", "+2 day")')
                return self.cursor.execute('''
                    SELECT * FROM Classes_Groups
                    WHERE start_time > date("2020-12-20", "+1 day")
                    AND start_time < date("2020-12-20", "+2 day")
                ''').fetchall()

    
    #получаем расписание студента id_stud на day_num дней 
    def get_stud_tmt(self, id_stud, day_num):
        day_str = "+" + str(day_num) + " day"
        with self.connection:
            return self.cursor.execute('''
                

                    SELECT Classes.name, Classes.type, Classes_Groups.start_time FROM Students

                    JOIN Groups_Students ON Students.id_student = Groups_Students.id_student
                    JOIN Groups ON Groups_Students.id_group = Groups.id_group

                    JOIN Classes_Groups ON Classes_Groups.id_group = Groups.id_group
                    JOIN Classes ON Classes.id_class = Classes_Groups.id_class

                    WHERE Students.id_student = ? 
                    AND Classes_Groups.start_time >= date("now")
                    AND Classes_Groups.start_time < date("now", ?)
                    ORDER BY Classes_Groups.start_time
            ''', (id_stud, day_str)).fetchall()

    #получаем группы студента
    def get_stud_groups(self, id_stud):
        with self.connection:
            return self.cursor.execute('''
                    SELECT Groups.id_group FROM Students

                    JOIN Groups_Students ON Students.id_student = Groups_Students.id_student
                    JOIN Groups ON Groups_Students.id_group = Groups.id_group
                    WHERE Students.id_student = ? 
                
            ''', (id_stud, )).fetchall()

    #происходит проверка есть ли такой студент с таким name и group (в будущем можно типа login password)
    #если есть, то смотрим записан ли там chat_id        если нету то возвращаем -2
    # если там "-", то тогда записываем туда chat_id
    #иначе возвращаем -1
    def register_stud(self, chat_id, name, group):
        #TODO
        pass

    #тоже самое, но с оператором
    def register_op(self, chat_id, name, email):
        #TODO
        pass

    #получить 1 ближайшую неподвержденную лекцию (в ближайшие 24ч) для данного chat_id.
    def get_top_class(self, chat_id):
        #TODO
        pass

    #сбросить все отметки данного оператора (== сделать поле confirmed у занятий 0)
    #о подтвержденности лекций на всех занятиях в ближайшие 24ч
    def abort_confirm(self, chat_id):
        #TODO
        pass

    
    #во первых проверить должен ли занятие class_id снимать оператор chat_id
    #если все норм то в данном занятии ставим confirmed = decision
    def confirm_class(self, chat_id, class_id, decision):
        #TODO
        pass


    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()