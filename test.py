from data_handler import SQLighter

db = SQLighter('lector.db')
#res = db.get_tmr_classes()
#for row in res:
#    print(row)
for c in db.get_tmr_classes('all'):
    print(c)