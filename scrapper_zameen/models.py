import os
import dotenv
from playhouse.postgres_ext import PostgresqlExtDatabase, ArrayField
from peewee import Model, AutoField, IntegerField, DoubleField, ForeignKeyField, TimestampField, CharField, DateField, BooleanField, TextField

dotenv.load_dotenv()
db = PostgresqlExtDatabase(
    os.environ.get("POSTGRES_DB"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    host=os.environ.get("POSTGRES_HOST"))


class BaseModel(Model):
    class Meta:
        database = db


class Property_Trend(BaseModel):
    id = AutoField()
    land_size = IntegerField()
    land_group = TextField()
    avg_price_per_sqft = IntegerField()
    avg_price = IntegerField()
    change_percentage = DoubleField()
    # latitude = DoubleField()
    # longitude = DoubleField()
    # location_title = TextField()
    # location_latitude = DoubleField()
    # location_longitude = DoubleField()
    type_id = IntegerField()
    purpose_id = IntegerField()


class Property_Trend_Index(BaseModel):
    id = AutoField()
    property = ForeignKeyField(Property_Trend, backref="property_indexes")
    month_year = TimestampField()
    value = IntegerField()
    avg_price_per_sqft = IntegerField()
    avg_price = IntegerField()
    change_percentage = IntegerField()


class Property_Trend_Change_Percentage_By_Price(BaseModel):
    id = AutoField()
    property = ForeignKeyField(
        Property_Trend, backref="property_change_percentage_by_price")
    month_year = TimestampField()
    value = IntegerField()
    avg_price_per_sqft = IntegerField()
    avg_price = IntegerField()
    change_percentage = IntegerField()


class Purpose(BaseModel):
    id = AutoField()
    title = CharField()
    alternate_title = CharField()


class Type(BaseModel):
    id = AutoField()
    title = CharField()
    alternate_title = CharField()


class Property_Trend_Change_Percentage_By_Price_Per_Sqft(BaseModel):
    id = AutoField()
    property = ForeignKeyField(
        Property_Trend, backref="property_change_percentage_by_price_per_sqft")
    month_year = TimestampField()
    value = IntegerField()
    avg_price_per_sqft = IntegerField()
    avg_price = IntegerField()
    change_percentage = IntegerField()


class Location(BaseModel):
    id = AutoField()
    title = CharField(max_length=255)
    title_l1 = CharField(max_length=255)
    longitude = DoubleField()
    latitude = DoubleField()
    level = IntegerField()
    is_popular = BooleanField()
    parent_id = IntegerField()
    position = IntegerField()
    prev_position = IntegerField()
    prev_search_percentage = DoubleField()
    search_percentage = DoubleField()
    view_count = IntegerField()


class Parent_Location(BaseModel):
    id = AutoField()
    level = IntegerField()
    name = CharField(max_length=255)
    name_l1 = CharField(max_length=255)

# Define the Trend model


class Trend(BaseModel):
    id = AutoField()
    location = ForeignKeyField(Location, backref="trends")
    month_year = CharField(max_length=20)
    stats_date = DateField()
    view_count = IntegerField()
    search_percentage = DoubleField()


class Parent_Location_With_ExternalID(Parent_Location):
    externalID = CharField()
    slug = CharField()
    slug_l1 = CharField()


class Property(BaseModel):
    id = AutoField()
    state = CharField()
    desc = TextField()
    purpose = CharField()
    price = DoubleField()
    product = CharField()
    title = CharField()
    title_l1 = CharField()
    rooms = CharField()
    baths = CharField()
    area = DoubleField()
    latitude = DoubleField(null=True)
    longitude = DoubleField(null=True)
    createdAt = TimestampField()
    updatedAt = TimestampField()
    location = ForeignKeyField(Parent_Location_With_ExternalID)
    price_history = ArrayField(field_class=IntegerField, default=[])


class Property_V2(BaseModel):
    id = AutoField()
    desc = TextField()
    header = TextField()
    type = CharField()
    price = CharField()
    location = CharField()
    bath = CharField()
    area = CharField()
    purpose = CharField()
    bedroom = CharField()
    added = TimestampField()
    initial_amount = CharField(null=True)
    monthly_installment = CharField(null=True)
    remaining_installments = CharField(null=True)
