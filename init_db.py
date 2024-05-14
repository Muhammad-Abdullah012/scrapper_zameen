import traceback
import sys
from typing import List, Any, Dict
from dateutil.parser import isoparse
from peewee import DoesNotExist
from models import (
    Failed,
    db,
    Location,
    Property_Trend,
    Property_Trend_Change_Percentage_By_Price,
    Property_Trend_Change_Percentage_By_Price_Per_Sqft,
    Parent_Location,
    Trend,
    Property_Trend_Index,
    Purpose,
    Type,
    Parent_Location_With_ExternalID,
    Property,
    Property_V2,
    BaseModel,
)


def init_db():
    db.connect(reuse_if_open=True)
    db.execute_sql(
        """CREATE OR REPLACE FUNCTION update_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;"""
    )
    tables_to_create: List[type[BaseModel]] = [
        Trend,
        Location,
        Parent_Location,
        Property_Trend,
        Property_Trend_Index,
        Purpose,
        Type,
        Parent_Location_With_ExternalID,
        Property,
        Property_V2,
        Property_Trend_Change_Percentage_By_Price,
        Property_Trend_Change_Percentage_By_Price_Per_Sqft,
    ]

    db.create_tables(tables_to_create)
    db.create_tables([Failed])
    db.execute_sql("ALTER TABLE property_v2 ADD COLUMN IF NOT EXISTS url text")
    tables_to_create.append(Failed)
    for table_class in tables_to_create:
        table_name = table_class._meta.name
        db.execute_sql(
            f"""
                ALTER TABLE {table_name}
                    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
            """
        )
        db.execute_sql(
            f"""
                CREATE OR REPLACE TRIGGER update_table_trigger BEFORE
                UPDATE ON {table_name} FOR EACH ROW
                EXECUTE PROCEDURE update_updated_at ();
            """
        )

    db.close()


def insert_popularity_trends(trends: dict):
    db.connect(reuse_if_open=True)
    try:
        if isinstance(trends, list):
            for t in trends:
                if not isinstance(t, dict):
                    continue
                id = t["id"]
                # location_id = t["location_id"]
                # month_year = t["month_year"]
                # stats_date = t["stats_date"]
                # view_count = t["view_count"]
                # search_percentage = t["search_percentage"]
                # print("id: ", id)
                # print("location_id: ", location_id)
                # print("month_year: ", month_year)
                # print("stats_date: ", stats_date)
                # print("view_count: ", view_count)
                # print("search_percentage: ", search_percentage)
                get_by_id = Trend.get_or_none(id=id)

                if get_by_id is None:
                    print("get_by_id is None")
                    Trend.create(**t)
                else:
                    print("get_by_id is Not None, updating record")
                    Trend.update(**t).where(Trend.id == id).execute()
                # Trend.get_or_create(**t)
            return

        print("insert_popularity_trends => ", trends)
        for k in trends["trends"].keys():
            try:
                print("trends[trends]: => ", trends["trends"])
                print("k ==> ", k)
                print("-----------------------")
                for popularity_trend in trends["trends"][k]:
                    print("popularity trends ==>> ", popularity_trend)
                    # print("popularity trends keys ==>> ", popularity_trend["id"])
                    print("_________----------------------_____________")
                    id = popularity_trend["id"]
                    parents = popularity_trend["parents"]
                    trends2 = popularity_trend["trends"]
                    # title = popularity_trend["title"]
                    # title_l1 = popularity_trend["title_l1"]
                    # longitude = popularity_trend["longitude"]
                    # latitude = popularity_trend["latitude"]
                    # level = popularity_trend["level"]
                    # is_popular = popularity_trend["is_popular"]
                    # parent_id = popularity_trend["parent_id"]
                    # position = popularity_trend["position"]
                    # prev_position = popularity_trend["prev_position"]
                    # search_percentage = popularity_trend["search_percentage"]
                    # prev_search_percentage = popularity_trend["prev_search_percentage"]
                    # view_count = popularity_trend["view_count"]
                    # print("id:", id)
                    # print("parents:", parents)
                    # print("trends:", trends)
                    # print("title:", title)
                    # print("title_l1:", title_l1)
                    # print("longitude:", longitude)
                    # print("latitude:", latitude)
                    # print("level:", level)
                    # print("is_popular:", is_popular)
                    # print("parent_id:", parent_id)
                    # print("position:", position)
                    # print("prev_position:", prev_position)
                    # print("search_percentage:", search_percentage)
                    # print("prev_search_percentage:", prev_search_percentage)
                    # print("view_count:", view_count)
                    print("_________----------------------_____________")
                    del popularity_trend["parents"]
                    del popularity_trend["trends"]

                    get_by_id = Location.get_or_none(id=id)
                    if get_by_id is None:
                        Location.create(**popularity_trend)
                    # Location.create(id=id, title=title, title_l1=title_l1, longitude=longitude,
                    # latitude=latitude, level=level, is_popular=is_popular,
                    # parent_id=parent_id, position=position,
                    # prev_position=prev_position,
                    # search_percentage=search_percentage,
                    # prev_search_percentage=prev_search_percentage,
                    # view_count=view_count)
                    for p in parents:
                        if not isinstance(p, dict):
                            continue
                        id = p["id"]
                        # level = p["level"]
                        # name = p["name"]
                        # name_l1 = p["name_l1"]
                        # print("id: ", id)
                        # print("level: ", level)
                        # print("name: ", name)
                        # print("name_l1: ", name_l1)
                        get_by_id = Parent_Location.get_or_none(id=id)
                        if get_by_id is None:
                            Parent_Location.create(**p)

                    for t in trends2:
                        if not isinstance(t, dict):
                            continue
                        id = t["id"]
                        # location_id = t["location_id"]
                        # month_year = t["month_year"]
                        # stats_date = t["stats_date"]
                        # view_count = t["view_count"]
                        # search_percentage = t["search_percentage"]
                        # print("id: ", id)
                        # print("location_id: ", location_id)
                        # print("month_year: ", month_year)
                        # print("stats_date: ", stats_date)
                        # print("view_count: ", view_count)
                        # print("search_percentage: ", search_percentage)
                        get_by_id = Trend.get_or_none(id=id)

                        if get_by_id is None:
                            print("get_by_id is None")
                            Trend.create(**t)
                            print("Created!!")
                        else:
                            print("get_by_id is Not None, updating record")
                            Trend.update(**t).where(Trend.id == id).execute()
                            print("Updated!!")

            except Exception as e:
                print(
                    f"insert_popularity_trends::for::Error: {e}", file=sys.stderr)
                print(f"trends ==> {trends}")
                traceback.print_exc()
                continue

    except Exception as e:
        print(f"insert_popularity_trends:::Error: {e}", file=sys.stderr)
        traceback.print_exc()

    finally:
        db.close()


def insert_area_trends(area_trends: dict):
    try:
        db.connect(reuse_if_open=True)
        index = area_trends["index"]
        print("index ==> ", index)
        if len(index.keys()) == 0:
            print("!!!!!!!!There is no key in index!!!!!!!")
            return
        key_value_obj: dict = {}
        id = index["id"]
        print("*************************************")
        for key, value in index.items():
            if (
                not isinstance(value, list)
                and not isinstance(value, dict)
                and value is not None
            ):
                key_value_obj[key] = value

        print("INSERTING VALUES IN property TABLE ==> ", key_value_obj)
        get_by_id = Property_Trend.get_or_none(id=id)
        if get_by_id is None:
            Property_Trend.create(**key_value_obj)
        else:
            Property_Trend.update(**key_value_obj).where(
                Property_Trend.id == id
            ).execute()

        for key, value in index.items():
            print("key => ", key, "value ==> ", value)
            print("isinstance(value, list): ", isinstance(value, list))
            print("isinstance(value, dict): ", isinstance(value, dict))
            if isinstance(value, list):
                if key == "index_values":
                    with db.atomic():
                        for v in value:
                            month_year = v["month_year"]
                            v["month_year"] = isoparse(month_year).timestamp()
                            v["property"] = id
                            get_by_id = Property_Trend_Index.get_or_none(
                                id=v.get("id"))
                            if get_by_id is None:
                                Property_Trend_Index.create(**v)
                            else:
                                Property_Trend_Index.update(**v).where(
                                    Property_Trend_Index.id == v.get("id")
                                ).execute()
                            # Property_Trend_Index.get_or_create(**v)
            elif isinstance(value, dict):
                if key == "purpose":
                    Purpose.get_or_create(**value)
                if key == "type":
                    Type.get_or_create(**value)
                if key == "change_percentage_by_price":
                    for k, v in value.items():
                        month_year = v["month_year"]
                        v["month_year"] = isoparse(month_year).timestamp()
                        v["property"] = id
                        print(
                            "values inserting in Property_Trend_Change_Percentage_By_Price => ",
                            v,
                        )
                        get_by_id = (
                            Property_Trend_Change_Percentage_By_Price.get_or_none(
                                id=v.get("id")
                            )
                        )
                        if get_by_id is None:
                            Property_Trend_Change_Percentage_By_Price.create(
                                **v)
                        else:
                            Property_Trend_Change_Percentage_By_Price.update(**v).where(
                                Property_Trend_Change_Percentage_By_Price.id
                                == v.get("id")
                            ).execute()
                        # Property_Trend_Change_Percentage_By_Price.get_or_create(
                        #     **v)
                if key == "change_percentage_by_price_per_sqft":
                    for k, v in value.items():
                        month_year = v["month_year"]
                        v["month_year"] = isoparse(month_year).timestamp()
                        v["property"] = id
                        print(
                            "values in Property_Trend_Change_Percentage_By_Price_Per_Sqft => ",
                            v,
                        )
                        get_by_id = Property_Trend_Change_Percentage_By_Price_Per_Sqft.get_or_none(
                            id=v.get("id")
                        )
                        if get_by_id is None:
                            Property_Trend_Change_Percentage_By_Price_Per_Sqft.create(
                                **v
                            )
                        else:
                            Property_Trend_Change_Percentage_By_Price_Per_Sqft.update(
                                **v
                            ).where(
                                Property_Trend_Change_Percentage_By_Price_Per_Sqft.id
                                == v.get("id")
                            ).execute()
                        # Property_Trend_Change_Percentage_By_Price_Per_Sqft.get_or_create(
                        #     **v)

    except Exception as e:
        print(f"insert_area_trends:::Error: {e}", file=sys.stderr)
        traceback.print_exc()
    finally:
        db.close()


def insert_queries_data(data: List[dict]):
    print("data to insert ==> ", data)
    try:
        db.connect(reuse_if_open=True)

        for item in data:
            try:
                location = item.get("location")
                if location is None:
                    print("No location found!!")
                    return
                for loc in location:
                    Parent_Location_With_ExternalID.get_or_create(**loc)
                print("location obj => ", location[-1])
                geography = item.get("geography", {"lat": None, "lng": None})

                # property_data = Property.select().where(Property.id == item.get("id")).first()
                # print("insert_queries_data:::property_data ==> ",
                #       property_data, file=open("property_data_logs.txt", "w"))
                # get_by_id = Property.get_by_id(item.get("id"))
                query = Property.select().where(Property.id == item.get("id"))
                try:
                    instance = query.get()
                    get_by_id = instance.__data__
                    if item["price"] != get_by_id["price"]:
                        get_by_id["price_history"].append(get_by_id["price"])
                        instance.save()
                        Property.update(
                            id=item["id"],
                            state=item["state"],
                            purpose=item["purpose"],
                            price=item["price"],
                            product=item["product"],
                            title=item.get("title", item.get("name", "")),
                            title_l1=item.get(
                                "title_l1", item.get("name_l1", "")),
                            rooms=item["rooms"],
                            baths=item["baths"],
                            area=item["area"],
                            latitude=geography["lat"],
                            longitude=geography["lng"],
                            createdAt=item.get("createdAt", 0),
                            updatedAt=item.get("updatedAt", 0),
                            desc=item.get(
                                "shortDescription", item.get("description", "")
                            ),
                            location_id=location[-1]["id"],
                        ).where(Property.id == item.get("id")).execute()
                    else:
                        print(
                            item["price"], " <= price is same => ", get_by_id["price"]
                        )
                except DoesNotExist:
                    Property.create(
                        id=item["id"],
                        state=item["state"],
                        purpose=item["purpose"],
                        price=item["price"],
                        product=item["product"],
                        title=item.get("title", item.get("name", "")),
                        title_l1=item.get("title_l1", item.get("name_l1", "")),
                        rooms=item["rooms"],
                        baths=item["baths"],
                        area=item["area"],
                        latitude=geography["lat"],
                        longitude=geography["lng"],
                        createdAt=item.get("createdAt", 0),
                        updatedAt=item.get("updatedAt", 0),
                        desc=item.get("shortDescription",
                                      item.get("description", "")),
                        location_id=location[-1]["id"],
                    )

                # if get_by_id is None:
                #     Property.create(id=item["id"],
                #                     state=item["state"],
                #                     purpose=item["purpose"],
                #                     price=item["price"],
                #                     product=item["product"],
                #                     title=item.get(
                #         "title", item.get("name", "")),
                #         title_l1=item.get(
                #         "title_l1", item.get("name_l1", "")),
                #         rooms=item["rooms"],
                #         baths=item["baths"],
                #         area=item["area"],
                #         latitude=geography["lat"],
                #         longitude=geography["lng"],
                #         createdAt=item.get("createdAt", 0),
                #         updatedAt=item.get("updatedAt", 0),
                #         desc=item.get(
                #         "shortDescription", item.get("description", "")),
                #         location_id=location[-1]["id"]
                #     )
                # else:
                #     if item["price"] != get_by_id["price"]:
                #         get_by_id["price_history"].append(get_by_id["price"])
                #         query.get().save()
                #         Property.update(id=item["id"],
                #                         state=item["state"],
                #                         purpose=item["purpose"],
                #                         price=item["price"],
                #                         product=item["product"],
                #                         title=item.get(
                #             "title", item.get("name", "")),
                #             title_l1=item.get(
                #             "title_l1", item.get("name_l1", "")),
                #             rooms=item["rooms"],
                #             baths=item["baths"],
                #             area=item["area"],
                #             latitude=geography["lat"],
                #             longitude=geography["lng"],
                #             createdAt=item.get("createdAt", 0),
                #             updatedAt=item.get("updatedAt", 0),
                #             desc=item.get(
                #             "shortDescription", item.get("description", "")),
                #             location_id=location[-1]["id"]
                #         ).where(Property.id == item.get("id")).execute()
                #     else:
                #         print(item["price"], " <= price is same => ",
                #               get_by_id["price"], file=open("price_init_db.txt", "a"))
                # Property.get_or_create(id=item["id"],
                #                        state=item["state"],
                #                        purpose=item["purpose"],
                #                        price=item["price"],
                #                        product=item["product"],
                #                        title=item.get(
                #                            "title", item.get("name", "")),
                #                        title_l1=item.get(
                #                            "title_l1", item.get("name_l1", "")),
                #                        rooms=item["rooms"],
                #                        baths=item["baths"],
                #                        area=item["area"],
                #                        latitude=geography["lat"],
                #                        longitude=geography["lng"],
                #                        createdAt=item.get("createdAt", 0),
                #                        updatedAt=item.get("updatedAt", 0),
                #                        desc=item.get(
                #                            "shortDescription", item.get("description", "")),
                #                        location_id=location[-1]["id"]
                #                        )
            except Exception as e:
                print(f"insert_queries_data::for::Error: {e}", file=sys.stderr)
                traceback.print_exc()
                continue

    except Exception as e:
        print(f"insert_queries_data::Error: {e}", file=sys.stderr)
        traceback.print_exc()
    finally:
        db.close()


def insert_property_data(data: Dict[str, Any]):
    print("insert_property_data::data==> ", data)
    try:
        url = data.get("url")
        db.connect(reuse_if_open=True)
        existing_property = Property_V2.get_or_none(url=url)
        if existing_property is not None:
            existing_property.update(**data).where(url=url).execute()
        else:
            Property_V2.create(**data)
    except Exception as e:
        print(f"insert_property_data::Error: {e}", file=sys.stderr)
        traceback.print_exc()
    finally:
        db.close()


def insert_failure_data(desc: str, url: str):
    try:
        db.connect(reuse_if_open=True)
        Failed.create(**{desc: desc, url: url})
    except Exception as e:
        print(f"insert_failure_data::Error: {e}", file=sys.stderr)
        traceback.print_exc()
    finally:
        db.close()
