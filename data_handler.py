# -*- coding: utf-8 -*-
import sqlite3
import shelve

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
    def get_stud_tmt(self, chat_id, day_num):
        day_str = "+" + str(day_num) + " day"
        with self.connection:
            return self.cursor.execute('''
                

                    SELECT Classes.name, Classes.type, Classes_Groups.start_time FROM Students

                    JOIN Groups_Students ON Students.id_student = Groups_Students.id_student
                    JOIN Groups ON Groups_Students.id_group = Groups.id_group

                    JOIN Classes_Groups ON Classes_Groups.id_group = Groups.id_group
                    JOIN Classes ON Classes.id_class = Classes_Groups.id_class

                    WHERE Students.chat_id = ? 
                    AND Classes_Groups.start_time >= date("now")
                    AND Classes_Groups.start_time < date("now", ?)
                    ORDER BY Classes_Groups.start_time
            ''', (chat_id, day_str)).fetchall()

    #получаем группы студента
    def get_stud_groups(self, id_stud):
        with self.connection:
            return self.cursor.execute('''
                    SELECT Groups.id_group FROM Students

                    JOIN Groups_Students ON Students.id_student = Groups_Students.id_student
                    JOIN Groups ON Groups_Students.id_group = Groups.id_group
                    WHERE Students.id_student = ? 
                
            ''', (id_stud, )).fetchall()


    #возвращаем chat_id студента по имени и группе
    def get_stud_chat_id(self, name, group):
        with self.connection:
            return self.cursor.execute('''
                    SELECT chat_id FROM Students
                    WHERE name = ? 
                    AND number_of_group = ?
                    ''', (name, group, )).fetchall()

    #возвращаем существущие chat_id 
    def get_stud_all_chat_id(self):
        with self.connection:
            return self.cursor.execute('''
                    SELECT chat_id FROM Students
                    WHERE chat_id != '-' 
                    ''').fetchall()


    #возвращаем chat_id оператора по имени и email
    def get_op_chat_id(self, name, email):
        with self.connection:
            return self.cursor.execute('''
                    SELECT chat_id FROM Operators
                    WHERE name = ? 
                    AND email = ?
                    ''', (name, email, )).fetchall()
    
    #возвращаем существущие chat_id 
    def get_op_all_chat_id(self):
        with self.connection:
            return self.cursor.execute('''
                    SELECT chat_id FROM Operators
                    WHERE chat_id != '-' 
                    ''').fetchall()



    # USER REGISTRATION
    # происходит проверка есть ли такой студент с таким name и group (в будущем можно типа login password)
    # для этого находим значение столбца chat_id студента с таким name и group
    # если значения нет (такого ученика нет), то возвращается False (0 case)
    # если есть, то смотрим записно ли в столбце chat_id значение отличное от "-"
    # если записано и оно неравно chat_id, то возвращаем False (1 case)
    # если записано и оно равно chat_id, то возвращаем это значение (2 case)
    # если записано и оно встречается в строке другого ученика, то возвращаем False (3 case)
    # если "-", то записываем chat_id и возвращаем записанное значение (4 case) 

    def register_stud(self, chat_id, name, group):

        chat_id_in_bd = self.get_stud_chat_id(name, group)
            
        if len(chat_id_in_bd) == 0:
            print("0 case")
            return False

        chat_id_in_bd = chat_id_in_bd[0][0]

        if chat_id_in_bd != '-' and chat_id_in_bd != str(chat_id):
            print("1 case")
            return False

        if chat_id_in_bd != '-':
            print("2 case")
            return self.cursor.execute('''
                    SELECT chat_id FROM Students
                    WHERE name = ? 
                    AND number_of_group = ?
                    ''', (name, group, )).fetchall()

        id_list = self.get_stud_all_chat_id()
        id_set = set(map(lambda x: x[0], id_list))
        
        if str(chat_id) in id_set:
            print("3 case")
            return False 

        print("4 case")
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



    #аналогичная регистрация оператора
    def register_op(self, chat_id, name, email):

        chat_id_in_bd = self.get_op_chat_id(name, email)

        if len(chat_id_in_bd) == 0:
            print("0 case")
            return False

        chat_id_in_bd = chat_id_in_bd[0][0]

        if chat_id_in_bd != '-' and chat_id_in_bd != str(chat_id):
            print("1 case")
            return False

        if chat_id_in_bd != '-':
            print("2 case")
            return self.cursor.execute('''
                    SELECT chat_id FROM Operators
                    WHERE name = ? 
                    AND email = ?
                    ''', (name, email, )).fetchall()

        id_list = self.get_op_all_chat_id()
        id_set = set(map(lambda x: x[0], id_list))

        if str(chat_id) in id_set:
            print("3 case")
            return False

        print("4 case")
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

    def get_all_queries(self, chat_id):
        with self.connection:
            return self.cursor.execute(''' 
                    SELECT DISTINCT Classes.id_class, Classes.confirmed FROM Operators

                    JOIN Classes_Operators ON Operators.id_operator = Classes_Operators.id_operator
                    JOIN Classes ON Classes_Operators.id_class = Classes.id_class

                    JOIN Classes_Groups ON Classes.id_class = Classes_Groups.id_class

                    WHERE Operators.chat_id = ? 
                    AND Classes_Groups.start_time >= date("2020-12-20")
                    AND Classes_Groups.start_time < date("2020-12-20", "+2 day")
                    ORDER BY Classes_Groups.start_time
            ''', (chat_id, )).fetchall()
    
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
        all_q = self.get_all_queries(chat_id)
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
    #полЫучить 1 ближайшую неподвержденную лекцию (в ближайшие 24ч) для данного chat_id.
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
