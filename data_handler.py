# -*- coding: utf-8 -*-
import sqlite3
import shelve
from hashlib import md5

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

    
    #получаем расписание юзера chat_id  на day_num дней 
    def stud_tmt(self, chat_id, day_num):
        day_str = "+" + str(day_num) + " day"
        with self.connection:
            return self.cursor.execute('''
        
                    SELECT Classes.name, Classes.type, Classes_Groups.start_time FROM Students

                    JOIN Groups_Students ON Students.id_student = Groups_Students.id_student
                    JOIN Groups ON Groups_Students.id_group = Groups.id_group

                    JOIN Classes_Groups ON Classes_Groups.id_group = Groups.id_group
                    JOIN Classes ON Classes.id_class = Classes_Groups.id_class

                    WHERE Students.chat_id = ?
                    AND Classes_Groups.start_time >= date("2020-12-19")
                    AND Classes_Groups.start_time < date("2020-12-19", ?)
                    ORDER BY Classes_Groups.start_time
            ''', (chat_id, day_str)).fetchall()
        
    #получаем дедлайны студента
    def stud_deadl(self, chat_id, day_num):
        day_str = "+" + str(day_num) + " day"
        with self.connection:
            return self.cursor.execute('''
                    SELECT Deadlines.name, Deadlines.time_date, Deadlines.link_to_folder_with_tasks FROM Deadlines
                    JOIN Groups_Deadlines ON Groups_Deadlines.id_deadline = Deadlines.id_deadline
                    JOIN Groups ON Groups.id_group = Groups_Deadlines.id_group

                    JOIN Groups_Students ON Groups_Students.id_group = Groups.id_group
                    JOIN Students ON Students.id_student = Groups_Students.id_student

                    WHERE Students.chat_id = ?
                    AND Deadlines.time_date >= date("2020-12-19")
                    AND Deadlines.time_date < date("2020-12-19", ?)

                    ORDER BY Deadlines.time_date
            ''', (chat_id, day_str, )).fetchall()
        

    #получаем группы студента
    def get_stud_groups(self, id_stud):
        with self.connection:
            return self.cursor.execute('''
                    SELECT Groups.id_group FROM Students

                    JOIN Groups_Students ON Students.id_student = Groups_Students.id_student
                    JOIN Groups ON Groups_Students.id_group = Groups.id_group
                    WHERE Students.id_student = ? 
                
            ''', (id_stud, )).fetchall()


    #USER REGISTRATION
    #происходит проверка есть ли такой студент с таким name и group (в будущем можно типа login password)
    #если есть, то смотрим записан ли там chat_id        если нету то возвращаем -2
    # если там "-", то тогда записываем туда chat_id
    #иначе возвращаем False
    #если успех True
    def register_stud(self, chat_id, name, group):
        #TODO
        with self.connection:
            self.cursor.execute('''
                    UPDATE Students SET chat_id = ? 
                    WHERE name = ? 
                    AND number_of_group = ?
            ''', (chat_id, name, group, ))

            return self.cursor.execute('''
                    SELECT chat_id FROM Students
                    WHERE name = ? 
                    AND number_of_group = ?
                    ''', (name, group, )).fetchall()



    #тоже самое, но с оператором
    def register_op(self, chat_id, name, email):
        #TODO
        with self.connection:
            self.cursor.execute('''
                    UPDATE Operators SET chat_id = ? 
                    WHERE name = ? 
                    AND email = ?
            ''', (chat_id, name, email, ))

            return self.cursor.execute('''
                    SELECT chat_id FROM Operators
                    WHERE name = ? 
                    AND email = ?
                    ''', (name, email, )).fetchall()


    #CUPTURE CONFIRM
    def get_all_queries(self, chat_id, days):
        day_str = "+" + str(days) + " day"
        with self.connection:
            return self.cursor.execute(''' 
                    SELECT DISTINCT Classes.id_class, Classes.name, Classes.type, Classes_Groups.start_time, Classes.confirmed FROM Operators

                    JOIN Classes_Operators ON Operators.id_operator = Classes_Operators.id_operator
                    JOIN Classes ON Classes_Operators.id_class = Classes.id_class

                    JOIN Classes_Groups ON Classes.id_class = Classes_Groups.id_class

                    WHERE Operators.chat_id = ? 
                    AND Classes_Groups.start_time >= date("2020-12-20")
                    AND Classes_Groups.start_time < date("2020-12-20", ?)
                    ORDER BY Classes_Groups.start_time
            ''', (chat_id, day_str, )).fetchall()
    
    def get_query(self, chat_id):
         with self.connection:
            return self.cursor.execute(''' 
                    SELECT DISTINCT Classes.id_class, Classes.name, Classes.type, MIN(Classes_Groups.start_time) FROM Operators
                    JOIN Classes_Operators ON Operators.id_operator = Classes_Operators.id_operator
                    JOIN Classes ON Classes_Operators.id_class = Classes.id_class

                    JOIN Classes_Groups ON Classes.id_class = Classes_Groups.id_class

                    WHERE Operators.chat_id = ? 
                    AND Classes_Groups.start_time >= date("2020-12-20")
                    AND Classes_Groups.start_time < date("2020-12-20", "+2 day")
                    AND Classes.confirmed == '0'
            ''', (chat_id, )).fetchall()
    
    #сбросить все отметки на след день
    def abort_confirm(self, chat_id):
        all_q = self.get_all_queries(chat_id, 2)
        for q in all_q:
            id_class = q[0]
            self.cursor.execute(''' 
                    UPDATE Classes SET confirmed = '0'
                    WHERE id_class = ?
            ''', (id_class, )).fetchall()

        return True
    
    #зафиксировать съемку лекции
    def commit(self, chat_id, dec):
        with self.connection:
            res = self.get_query(chat_id)

            if res[0][0] is None:
                return False
            else:
                commit_id = res[0][0]
                self.cursor.execute(''' 
                    UPDATE Classes SET confirmed = ?
                    WHERE id_class = ?
                ''', (dec, commit_id, )).fetchall()
                return True

    #SET DEADLINE
    def set_deadline(self, class_id, chat_id, text, time):
        with self.connection:
            op_id = self.cursor.execute(''' 
                    SELECT id_operator FROM Operators
                    WHERE chat_id = ?
                ''', (chat_id, )).fetchall()
            if op_id and op_id[0][0] is not None:
                op_id = op_id[0][0]
            else:
                return False
            
            deadl_id = md5(text.encode()).hexdigest()
            
            self.cursor.execute(''' 
                    INSERT INTO Deadlines VALUES
                    (?, ?, ?, '-', DATE("now"), ?)
                ''', (deadl_id, str(time), text, op_id, )).fetchall()
            groups = self.cursor.execute(''' 
                    SELECT id_group FROM Classes_Groups
                    WHERE id_class = ?
                ''', (class_id, )).fetchall()
            
            for g in groups:
                id_group = g[0]
                self.cursor.execute(''' 
                    INSERT INTO Groups_Deadlines VALUES
                    (?, ?)
                ''', (id_group, deadl_id, )).fetchall()
            
            return True

    
    def check(self, chat_id):
        #TODO
        #sql запрос к таблице Students есть ли там такой chat_id
        #sql запрос к таблице Operators есть ли там такой chat_id
        #если этот пользователь есть олько в Students  то вернуть 'stud'
        #если только в Operators  то вернуть 'op'
        #если и там и там 's/o'
        #если нигде 'unreg'
        return 'unreg'



    #OPERATORS CONFIRMATIONS
    #получить 1 ближайшую неподвержденную лекцию (в ближайшие 24ч) для данного chat_id.
    def get_top_class(self, chat_id):
        #TODO
        pass

    #сбросить все отметки данного оператора (== сделать поле confirmed у занятий 0)
    #о подтвержденности лекций на всех занятиях в ближайшие 24ч
    #def abort_confirm(self, chat_id):
    #    #TODO
    #    pass
    
    #во первых проверить должен ли занятие class_id снимать оператор chat_id
    #если все норм то в данном занятии ставим confirmed = decision
    def confirm_class(self, chat_id, class_id, decision):
        #TODO
        pass


    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()