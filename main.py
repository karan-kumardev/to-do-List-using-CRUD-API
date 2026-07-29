## Week 2 Task-- CRUD using FastAPI
import psycopg
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

class Tasks(BaseModel):
    title:str
    done:bool=False

conn=psycopg.connect(DATABASE_URL)
app=FastAPI()
cursor=conn.cursor() # creating cursor to execute operations


cursor.execute("""CREATE TABLE if not exists TASKS( 
                    
                  id serial primary key,
                  title text,
                  done boolean  
                  )

            """)

cursor.execute("select count(*) from tasks")
count = cursor.fetchone()[0]

if count == 0:
    cursor.execute("insert into tasks (title, done) values (%s, %s)", ("Buy milk", False))
    cursor.execute("insert into tasks (title, done) values (%s, %s)", ("Read book", False))
    cursor.execute("insert into tasks (title, done) values (%s, %s)", ("Clean room", False))
    conn.commit()


@app.get("/")
def root():
     return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/tasks/{id}")
def read(id:int):

   
    cursor.execute("select * from tasks where id = %s ",(id,))
    result= cursor.fetchone() 
    
    if result is None:
     raise HTTPException(status_code=404, detail=f"Task {id} not found")
   
    return {"id":result[0], "title":result[1], "done":bool(result[2])}



@app.get("/tasks")
def get_all():

  cursor.execute("select * from tasks")
  data=cursor.fetchall()

  record=[]

  for rows in data:
     record.append({"id":rows[0],"title":rows[1],"done":bool(rows[2])})  

  return record



@app.post("/tasks", status_code=201)
def add_tasks(new_task:Tasks):

   if new_task.title != "": 
     cursor.execute("insert into tasks (title, done) values (%s, %s) returning *",(new_task.title,False) )
     new_row=cursor.fetchone()
     conn.commit()
     return {"id":new_row[0],"title":new_row[1],"done":bool(new_row[2])}
   else:
       raise HTTPException(status_code=400,detail="Empty Body ") 
        
        
    
@app.delete("/tasks/{id}",status_code=204)
def delete(id:int):

    cursor.execute("delete from tasks where id=%s",(id,))
    conn.commit()
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="not found")      
    


@app.put("/tasks/{id}")
def update(id:int,task:Tasks):


        if task.title!="":
         cursor.execute("update tasks set title=%s, done=%s where id=%s",(task.title,task.done,id,))
         conn.commit()
        
        else:
            raise HTTPException(status_code=400,detail="invalid body")

        if cursor.rowcount==0:
          raise HTTPException(status_code=404, detail="Not found")


        return {"id":id,"title":task.title,"done":task.done}

