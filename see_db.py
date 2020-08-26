from dbmanager import DBManager

db = DBManager("data/elrondStats.db")

d = db.get_ids()

print(d)
