from sqlmodel import Field, SQLModel, Session, create_engine, select, Relationship
from fastapi import Depends
from datetime import datetime, timedelta
from faker import Faker
from typing import Annotated, List


# tabels for the database
class person(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firstname: str = Field(index=True)
    lastname: str = Field(index=True)
    secret_number: int | None = Field(default=None, index=True)
    age: int | None = Field(default=None, index=True)
    attendances: List["time"] = Relationship(back_populates="person")

class time(SQLModel, table=True):
    time_id: int | None = Field(default=None, primary_key=True)
    person_id: int = Field(foreign_key="person.id")
    clock_in: datetime = Field(default_factory=datetime.now)
    clock_out: datetime | None = Field(default=None)
    total_time: int | None = Field(default=None, index=True)
    person: "person" = Relationship(back_populates="attendances")

#setup and creation of the database 
sqllite_fil_name = "db.db"
sqllite_url = f"sqlite:///app/{sqllite_fil_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqllite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]




# Creates fake date

fake = Faker('sv_SE') 

def create_fake_data(engine, num_people=200):
    with Session(engine) as session:
        statement = select(person)
        first_person = session.exec(statement).first()

        if first_person:
            print("Databasen är redan fylld, hoppar över fake data.")
            return 

        print(f"Skapar {num_people} stycken fake-personer...")
        
        for _ in range(num_people):
            new_person = person(
                firstname=fake.first_name(),
                lastname=fake.last_name(),
                secret_number=fake.random_int(min=1000, max=9999),
                age=fake.random_int(min=18, max=80)
            )
            session.add(new_person)
            session.commit() 
            session.refresh(new_person)

            if new_person.id is not None:
                for _ in range(4): 
                    start_time = fake.date_time_this_month()
                    random_hours = fake.random_int(min=4, max=13)
                    duration = timedelta(hours=random_hours) 
                    end_time = start_time + duration

                    new_time = time(
                        person_id=new_person.id, 
                        clock_in=start_time,
                        clock_out=end_time,
                        total_time=int(duration.total_seconds() / 60)
                    )
                    session.add(new_time) 
        session.commit()
        print("Fake data har skapats framgångsrikt!")