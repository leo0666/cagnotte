from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import aiomysql, argon2, datetime

from lib.db import get_db
from lib.env import ACCESS_TOKEN_EXPIRE, REFRESH_TOKEN_EXPIRE
from lib.token import create_jwt_token
from shema.user_login import UserLogin
from shema.user_register import UserRegister

PH = argon2.PasswordHasher(
    time_cost=4,
    memory_cost=65536,   # 64 Mo
    parallelism=2,
    hash_len=32,
    salt_len=16
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session")
    return response

# Route GET : afficher le formulaire
@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route POST : traitement du formulaire
@router.post("/login")
async def login_post(request: Request, user : UserLogin, conn : aiomysql.Connection = Depends(get_db)):

    cursor = await conn.cursor(aiomysql.DictCursor)

    query = "SELECT id, pwd FROM User WHERE username = %s"
    data = (user.username,)

    await cursor.execute(query, data)

    rep_user = await cursor.fetchone()

    if not rep_user:
        return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "This username doesn't exist"
        })
    
    try:
        PH.verify(rep_user['pwd'], user.pwd)

        access_token, access_exp = await create_jwt_token({"id_user": rep_user['id']}, ACCESS_TOKEN_EXPIRE)
        
        refresh_token, refresh_exp = await create_jwt_token({"id_user": rep_user['id']}, REFRESH_TOKEN_EXPIRE)

        query_verif_row_token = "SELECT id_user FROM Token WHERE id_user = %s;"
        data_verif_row_token = (rep_user['id'],)
                
        await cursor.execute(query_verif_row_token, data_verif_row_token)

        rep_verif_row_token = await cursor.fetchone()

        if not rep_verif_row_token:
            try:
                query_insert_tokens = """
                            INSERT INTO Token(id_user, access_token, refresh_token, expire_access_token, expire_refresh_token)
                            VALUES (%s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                access_token = VALUES(access_token),
                                refresh_token = VALUES(refresh_token),
                                expire_access_token = VALUES(expire_access_token), 
                                expire_refresh_token = VALUES(expire_refresh_token);"""
                data_insert_tokens = (rep_user['id'], access_token, refresh_token, access_exp, refresh_exp)

                await cursor.execute(query_insert_tokens, data_insert_tokens)

                if cursor.rowcount < 1:
                    return templates.TemplateResponse("login.html", {
                    "request": request,
                    "error": "Erreur lors de l'insertion des token"
                })

                await conn.commit()

                response = RedirectResponse(url="/", status_code=302)
                response.set_cookie(key="session", value=f"{access_token}", expires=access_exp.replace(tzinfo=datetime.timezone.utc))
                return response
                    
            except Exception as e:
                await conn.rollback()
                return templates.TemplateResponse("login.html", {
                "request": request,
                "error": f"Erreur lors de l'insertion des token : {e}"
                })

        else:
            try:
                query = """
                            UPDATE
                                Token 
                            
                            SET 
                                access_token = %s, refresh_token = %s, expire_access_token = %s, expire_refresh_token = %s  
                                
                            WHERE 
                                id_user = %s;"""
                data = (access_token, refresh_token, access_exp, refresh_exp, rep_user['id'])

                await cursor.execute(query, data)

                if cursor.rowcount < 1:
                    return templates.TemplateResponse("login.html", {
                    "request": request,
                    "error": f"Erreur lors de l'insertion des token"
                })

                await conn.commit()

                response = RedirectResponse(url="/", status_code=302)
                response.set_cookie(key="session", value=f"{access_token}", expires=access_exp.replace(tzinfo=datetime.timezone.utc))
                return response
                    
            except Exception as e:
                await conn.rollback()
                return templates.TemplateResponse("login.html", {
                "request": request,
                "error": f"Erreur lors de l'insertion des token : {e}"
                })
    
    except argon2.exceptions.VerifyMismatchError:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Username or password invalid"
        })

@router.get("/register")
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_post(request: Request, user : UserRegister, conn : aiomysql.Connection = Depends(get_db)):
    cursor = await conn.cursor(aiomysql.DictCursor)

    query = "SELECT id FROM User WHERE email = %s;"
    data = (user.email,)

    await cursor.execute(query, data)

    exist_email = await cursor.fetchone()
    
    if exist_email:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Email déjà utilisé."
        })
    try:
        hashed_pwd = PH.hash(user.pwd)
        
        query = """
                INSERT INTO 
                    User(first_name, last_name, email, username, pwd)
                
                VALUES
                    (%s, %s, %s, %s, %s);"""
        data = (user.first_name, user.last_name, user.email, user.username, hashed_pwd)

        await cursor.execute(query, data)

        await conn.commit()

        return RedirectResponse("/login", status_code=303)
    
    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": f"Erreur : {e}"
        })