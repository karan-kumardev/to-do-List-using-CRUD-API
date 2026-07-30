from supabase import Client, create_client
from dotenv import load_dotenv
import os
from fastapi import APIRouter, HTTPException,Header
from pydantic import BaseModel


class User(BaseModel):
    email:str
    password:str


auth=APIRouter()
open_router=APIRouter()
load_dotenv()

store=[{"email":"","password":""}]

supabase_key=os.environ.get("SUPABASE_KEY")
supabase_url=os.environ.get("SUPABASE_URL")

supabase:Client =create_client(supabase_url,supabase_key)

@auth.post("/signup",status_code=201)
def add_user(new_user:User):

    if not new_user.email or not new_user.password:
        raise HTTPException(status_code=400,detail="password and email required")


    try:
        response= supabase.auth.sign_up({
            "email":new_user.email,
            "password":new_user.password
        })
        return response
    except:
        raise HTTPException(status_code=400, detail="Password and email required")



@auth.post("/login",status_code=200)
def login(user:User):

    if not user.email or not user.password:
        raise HTTPException(status_code=400, detail="Must fill both fields")

    try:
        response=supabase.auth.sign_in_with_password({"email":user.email,
                                         "password":user.password
                                        })

        return response
    except:
        raise  HTTPException(status_code=401, detail="Non Existing User")   

@open_router.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}    

@open_router.get("/protected/profile")
def profile(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token required")

    token = authorization.split(" ")[1]

    try:
        user_response = supabase.auth.get_user(token)
        return user_response
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")