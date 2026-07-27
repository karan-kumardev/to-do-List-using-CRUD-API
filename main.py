## Week 2 Task-- CRUD using FastAPI
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class Tasks(BaseModel):
    title:str

conn=sqlite3.connect("to_do.db",check_same_thread=False) # connecting sqlite to this file
app=FastAPI()
cursor=conn.cursor() # creating cursor to execute operations


cursor.execute("""CREATE TABLE if not exists TASKS( 
                    
                  id integer primary key,
                  title text,
                  done Bool  
                  )

            """)



@app.get("/")
def root():
     return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

# @app.get("/tasks/{id}")
# def read(id:int):
    
#     for target in storage:
#         if target.get("id")==id:
#             return target
    
#     raise HTTPException(status_code=404, detail=f"Task {id} not found")


# @app.get("/tasks")
# def get_all():

#     return storage


@app.post("/tasks", status_code=201)
def add_tasks(new_task:Tasks):

   if new_task.title != "": 
     cursor.execute("insert into tasks (title, done) values (?,?)",(new_task.title,False) )
     conn.commit()
     id=cursor.lastrowid
     return {"id":id, "title":new_task.title,"done":False}  
   else:
       raise HTTPException(status_code=400,detail="Empty Body ") 
        
        
    
