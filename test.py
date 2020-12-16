from data_handler import SQLighter
import shelve
from telebot import types

#with shelve.open('shelve.db') as storage:
#    print(storage['80271002'])

db = SQLighter('lector.db')
print(db.abort_confirm(80271002))
print(db.get_query(80271002))
#print(db.commit(80271002, '1'))
#print(db.get_query(80271002))
#print(db.commit(80271002, '1'))
#print(db.get_query(80271002))
#