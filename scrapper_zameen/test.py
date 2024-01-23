from init_db import db, Property

db.connect(reuse_if_open=True)

query = Property.select().where(Property.id == 45373)
get_by_id = query.get()
data = get_by_id.__data__
data["price_history"].append(data["price"])
get_by_id.save()
Property.update(price=10).where(Property.id == 45373).execute()

db.close()
