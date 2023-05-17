from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import URL
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from sqlalchemy import text, Date
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy import func
from sqlalchemy import table, column
import sqlalchemy.pool as pool

import psycopg2

from sqlalchemy import create_engine
from config import config
from datetime import date

from tabulate import tabulate


# Declare ORM Model for each table
class Base(DeclarativeBase):
    pass


class Requirement(Base):
    __tablename__ = "requirements"

    state: Mapped[str] = mapped_column(String(30), primary_key=True)
    region: Mapped[str] = mapped_column(String(30), primary_key=True)
    use: Mapped[str] = mapped_column(String(30), primary_key=True)

    raw: Mapped[str] = mapped_column(String(300))

    spaces_per: Mapped[Optional[float]] = mapped_column()
    unit_quantity: Mapped[Optional[float]] = mapped_column()
    unit: Mapped[Optional[str]] = mapped_column(String(30))

    # misc: Mapped[Optional[JSONB]] = mapped_column()

    def __repr__(self) -> str:
        return f"Requirement(state={self.state}, region={self.region}, use={self.use}, raw={self.raw})"

    def __iter__(self):
        yield self.state
        yield self.region
        yield self.use
        yield self.raw
"""
class Region_Info(Base):
    __tablename__ = "region_info"

    state: Mapped[str] = mapped_column(String(30), primary_key=True)
    region: Mapped[str] = mapped_column(String(30), primary_key=True)
    date: Mapped[date] = mapped_column(Date)
    url: Mapped[str] = mapped_column(String(200))

    def __repr__(self) -> str:
        return f"Region_Info(state={self.state}, region={self.region}, date={self.date}, url={self.url})"
"""

# add = Requirement(state="CA", region="Los Angeles County", use="Bowling alleys", raw="3 spaces per bowling alley.")


def insert_df(df, state, region):
    object_list = []
    for row in df.values.tolist():
        object_list.append(Requirement(state=state, region=region, use=row[0], raw=row[1]))

    for i in object_list:
        print(repr(i))

    input("Press Enter to continue with insertion into database.")

    url_object = URL.create(**config())
    engine = create_engine(url_object)

    with Session(engine) as session:
        print("Connecting to database...")
        session.add_all(object_list)

        # Need to find a way to deal with duplicates (either do nothing or update)
        # session.execute(insert(Requirement).values(regular_list).on_conflict_do_nothing())

        session.commit()
        statement = select(func.count()).select_from(table('requirements', column('use')))
        query = session.scalars(statement).all()
        print(f"Success. Total entries: {query}")


def test_connection():
    print("Testing connection to database.")
    url_object = URL.create(**config(section='postgresql+psycopg2'))

    engine = create_engine(url_object, pool_pre_ping=True, pool_recycle=3600)
    print(f"Database Connection Info: {url_object}")

    with Session(engine) as session:
        print("Attempting querying database.")
        statement = select(func.count()).select_from(table('requirements', column('use')))
        query = session.scalars(statement).all()
        print(query)


def test_pool_connection():
    print("Testing pool connection to database.")

    c = psycopg2.connect(user='postgres', host='db.ivzidqccueblykefgvbg.supabase.co', dbname='postgres')

    my_pool = pool.QueuePool(c, max_overflow=10, pool_size=5)
    print(f"Database Connection Info: {c}")

    conn = my_pool.connect()
    cursor_obj = conn.cursor()
    print("Attempting querying database.")
    statement = select(func.count()).select_from(table('requirements', column('use')))
    query = cursor_obj.scalars(statement).all()
    print(query)

    conn.close()


def read_database():
    print("Connecting to database...")
    url_object = URL.create(**config())
    engine = create_engine(url_object)
    user = ""
    with Session(engine) as session:
        while user != "4":
            user = input("""-----------------------------------------------------------
            Enter number for command:
                (1) Show all
                (2) Filter
                (3) Count
                (4) Exit
                >>> """)
            if user == "1":
                statement = select(Requirement)
                print("Fetching all entries.")
                # print(f"Query: {statement}")
                result = session.scalars(statement).all()
                #print(result)
                #result = [r[0] for r in result]
                print(tabulate(result, headers=["state", "region", "use", "raw"], tablefmt='grid',
                               maxcolwidths=[None, None, 20, 20]))
            elif user == "2":
                if input("""
                (1) Filter by State
                (2) Filter by Region
                >> """) == "1":
                    result = session.query(Requirement.state).distinct().all()
                    print(tabulate(result, headers=["Available states"], tablefmt='grid'))
                    filter_state = input(
                        """Filter by State: """)
                    try:
                        statement = select(Requirement).filter_by(state=filter_state)
                        result = session.scalars(statement).all()
                        print(tabulate(result, headers=["state", "region", "use", "raw"], tablefmt='grid',
                                       maxcolwidths=[None, None, 20, 20]))
                    except IndexError:
                        print(f"There's no state by the name '{filter_state}'")
                else:
                    result = session.query(Requirement.region).distinct().all()
                    print(tabulate(result, headers=["Available regions"], tablefmt='grid'))
                    filter_region = input(
                        """Filter by Region: """)
                    try:
                        statement = select(Requirement).filter_by(region=filter_region)
                        result = session.scalars(statement).all()
                        print(tabulate(result, headers=["state", "region", "use", "raw"], tablefmt='grid',
                                       maxcolwidths=[None, None, 20, 20]))
                    except IndexError:
                        print(f"There's no region by the name '{filter_region}'")

            elif user == "3":
                statement = select(func.count()).select_from(table('requirements', column('use')))
                print("Fetching count.")
                query = session.scalars(statement).all()
                print(f"Total number of entries: {query}")


"""
def insert_region(state, region, url):
    url_object = URL.create(**config())
    # print(url_object)
    engine = create_engine(url_object)

    region_object = Region_Info(state=state, region=region, date=date.today(), url=url)

    with Session(engine) as session:
        session.add(region_object)
"""
