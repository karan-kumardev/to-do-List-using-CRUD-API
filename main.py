## Week 2 Task-- CRUD using FastAPI

from fastapi import FastAPI, HTTPException

app=FastAPI()

storage=[{"id":1, "task":"work", "status":"done"},
         {"id":2, "task":"watch movie", "status":"pending"},
         {"id":3, "task":"cook","status":"pending"}
        ]

@app.get("/tasks/{id}")
def read(id:int):
    
    for target in storage:
        if target.get("id")==id:
            return target
    
    raise HTTPException(status_code=404, detail=f"Task {id} not found")


@app.get("/tasks")
def get_all():

    return storage