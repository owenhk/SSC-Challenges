import fastapi
from fastapi import FastAPI, Request
import aiohttp
import asyncpg
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI()
pool: asyncpg.Pool = None

@app.on_event('startup')
async def startup():
    global pool
    url = os.getenv('DATABASE_URL')
    pool = await asyncpg.create_pool(
        url,
        max_size=20
    )


@app.get('/coreconcepts/1/getfact')
async def get_fact(request: Request):
    # Get the fact
    async with aiohttp.ClientSession() as session:
        async with session.get("https://uselessfacts.jsph.pl/api/v2/facts/random") as response:
            json_data = await response.json()
            fact = json_data["text"]
            # Create a random security code
            security_code = os.urandom(24).hex()
    # Save the fact and security code in the database
    async with pool.acquire() as connection:
        await connection.execute("""
        INSERT INTO facts (fact, security_code) VALUES ($1, $2)
        """, fact, security_code)
    return {
        "fact": fact,
        "Authorization": security_code
    }

@app.post("/coreconcepts/1/uploadfact")
async def upload_fact(request: Request):
    # Get the fact, which was sent in the request body
    data = await request.json()
    fact = data.get("fact")
    # Get header
    security_code = request.headers.get("Authorization")
    # Check if the security code is valid
    async with pool.acquire() as connection:
        result = await connection.fetchrow("""
        SELECT * FROM facts WHERE fact = $1
        """, fact)
        if result is None:
            raise fastapi.HTTPException(status_code=404, detail="Fact not found. Are you sure you sent the case sensitive fact?")
        security_code_test = result[2]
        if security_code_test != security_code:
            raise fastapi.HTTPException(status_code=403, detail="You sent the right fact - good job! - but the security code is wrong. It needs to be in the \"Authorization\" field of your request header.")
    # If the security code is valid, delete the fact from the database
    async with pool.acquire() as connection:
        await connection.execute("""
        DELETE FROM facts WHERE fact = $1
        """, fact)
    return {"success": True, "message": "Congratulations! You completed this challenge. It was a hard one!"}
