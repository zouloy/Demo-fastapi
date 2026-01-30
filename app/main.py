from fastapi import FastAPI,  Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
from sqlmodel import text, Session
from .db import create_db_and_tables, create_fake_data, engine, SessionDep, engine, person, time
import os
from dotenv import load_dotenv

# set upp of the backend
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    create_fake_data(engine, 200)
    yield

# Simple API set up for poc
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

app = FastAPI(lifespan=lifespan)
load_dotenv()
API_KEY = os.getenv("api_key")


def get_api_key(api_key: str = Security(api_key_header)):
    print(API_KEY)
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Ogiltig API-nyckel"
    )

@app.get("/")
def hello_world():
    return {"message": "OK"}


# example sql qureys for api
@app.get("/report/per-person-time")
def get_total_time(session: SessionDep, _auth=Depends(get_api_key)):
    query = text("""
            SELECT 
                p.firstname,
                p.lastname,
                p.secret_number,
                sum(t.total_time) as grand_total_minutes
            from person p
            JOIN time t ON p.id = t.person_id
            GROUP BY p.id
        """)
    
    results = session.exec(query).all()

    return [
        {
            "name": f"{row.firstname} {row.lastname}",
            "Number": row.secret_number,
            "total_minutes": row.grand_total_minutes
        } for row in results
    ]

@app.get("/reports/most-time-this-month")
def get_top_workers(session: SessionDep, _auth=Depends(get_api_key)):
    query = text("""
        SELECT 
            p.firstname || ' ' || p.lastname as full_name,
            p.secret_number, 
            SUM(t.total_time) / 60 as total_hours
        FROM person p
        JOIN time t ON p.id = t.person_id
        WHERE strftime('%m', t.clock_in) = strftime('%m', 'now')
        GROUP BY p.id
        ORDER BY total_hours DESC
        LIMIT 10
    """)
    results = session.exec(query).all()
    return [dict(row._mapping) for row in results]