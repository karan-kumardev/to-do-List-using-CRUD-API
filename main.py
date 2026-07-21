## Week 2 Task-- CRUD using FastAPI

from fastapi import FastAPI

app=FastAPI()

@app.get("/hello/{name}")
def read(name):
    return {"message":f"Hello,{name} using hello field"}