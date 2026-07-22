## Week 2 Task-- CRUD using FastAPI

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class Tasks(BaseModel):
    title:str

app=FastAPI()

storage=[{"id":1, "task":"work", "status":"done"},
         {"id":2, "task":"watch movie", "status":"pending"},
         {"id":3, "task":"cook","status":"pending"}
        ]

highest_id=3

@app.get("/")
def root():
     return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/tasks/{id}")
def read(id:int):
    
    for target in storage:
        if target.get("id")==id:
            return target
    
    raise HTTPException(status_code=404, detail=f"Task {id} not found")


@app.get("/tasks")
def get_all():

    return storage


@app.post("/tasks", status_code=201)
def add_tasks(new_tasks:Tasks):
    global highest_id
    highest_id+=1
    next={"id":highest_id,
            "tasks":new_tasks.title,
            "status":"pending"
        }

    if new_tasks.title != "":
        storage.append(next)
        return next
        
    else:
        highest_id-=1
        raise HTTPException(status_code=400, detail="Empty title")    
    

@app.put("/tasks/{id}")
def update(id:int,task:Tasks):

    for target in storage:
        if target.get("id")==id:
          if task.title != '':
              target["task"]=task.title

              return target
          else:
            raise HTTPException(status_code=400,detail="invalid body")

    raise HTTPException(status_code=404, detail="Not found")



@app.delete("/tasks/{id}",status_code=204)
def delete(id:int):

    for target in storage:

        if target.get("id")==id:
            storage.remove(target)
            return
    else:    
        raise HTTPException(status_code=404, detail="not found")        