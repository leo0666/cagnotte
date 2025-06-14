from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import aiomysql

from lib.db import db_connect, get_db
from lib.token import jwt_required
from shema.cagnotte_add import CagnotteAdd
from shema.cagnotte_edit import CagnotteEdit
from shema.cagnotte_del import CagnotteDel

router = APIRouter()
templates = Jinja2Templates(directory="templates")


async def calc_total_amount(cagnottes: list):
    async with db_connect() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            list_total_amount = {}
            for i in cagnottes:
                total_amount = 0
                

                id_cagnotte = i['id']

                if i['participants']:

                    for participant in i['participants']:
                        total_amount += participant['amount']
                    
                list_total_amount.setdefault(id_cagnotte, total_amount)

                query = """
                        UPDATE 
                            Cagnotte_
                        
                        SET 
                            total_amount = %s
                        
                        WHERE
                            id_cagnotte = %s;"""
                data = (total_amount, id_cagnotte)

                try:
                    await cursor.execute(query, data)
                    
                    if cursor.rowcount < 1:
                        raise
                    
                    await conn.commit()
                    continue
                
                except:
                    await conn.rollback()
                    continue
                
            return list_total_amount

@router.post("/cagnotte/add", response_class=HTMLResponse)
async def cagnotte_add(request: Request, cagnottes_: list[CagnotteAdd], conn : aiomysql.Connection = Depends(get_db)):
    token = request.cookies.get("session")
    
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_data = await jwt_required(token, conn)
    except:
        return RedirectResponse(url="/login", status_code=302)

    cursor = await conn.cursor(aiomysql.DictCursor)

    try:
        print(cagnottes_)
        for cagnotte in cagnottes_:

            query = "INSERT INTO Cagnotte_(id_user, name, description) VALUES (%s, %s, %s)"
            data = (user_data['id_user'], cagnotte.name, cagnotte.description)
            
            await cursor.execute(query, data)
        
        await conn.commit()

        return RedirectResponse(url="/", status_code=302)
    
    except Exception as e:
        await conn.rollback()

        query = """
        SELECT DISTINCT 
            Cagnotte_.id, Cagnotte_.name, Cagnotte_.description
        
        FROM 
            Cagnotte_
        
        WHERE Cagnotte_.id_user = %s;
    """
        data = (user_data['id_user'])
        
        await cursor.execute(query, data)

        cagnottes = await cursor.fetchall()

        query = """
            SELECT DISTINCT 
                Participant.id, Participant.id_cagnotte, Participant.first_name, Participant.last_name, Participant.amount
            
            FROM 
                Cagnotte_
            
            INNER JOIN
                Participant ON Cagnotte_.id = Participant.id_cagnotte
            
            WHERE Cagnotte_.id_user = %s;
        """
        data = (user_data['id_user'])
        
        await cursor.execute(query, data)

        participants = await cursor.fetchall()

        participants_by_cagnotte = {}

        for participant in participants:
            participants_by_cagnotte.setdefault(participant["id_cagnotte"], []).append(participant)

        # Ajout des participants dans chaque cagnotte
        for cagnotte in cagnottes:
            cagnotte["participants"] = participants_by_cagnotte.get(cagnotte["id"], [])
        
        list_total_amount = await calc_total_amount(cagnottes)

        for cagnotte in cagnottes:
            cagnotte["total_amount"] = list_total_amount.get(cagnotte["id"], [])
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "cagnottes": cagnottes,
            "error": f"Erreur lors de l'ajout {'de la cagnotte' if len(cagnottes_) == 1 else 'des cagnottes'} : {e}"
        })

@router.put("/cagnotte/edit", response_class=HTMLResponse)
async def cagnotte_edit(request: Request, cagnottes_: list[CagnotteEdit], conn : aiomysql.Connection = Depends(get_db)):
    token = request.cookies.get("session")
    
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_data = await jwt_required(token, conn)
    except:
        return RedirectResponse(url="/login", status_code=302)

    cursor = await conn.cursor(aiomysql.DictCursor)

    try:

        for cagnotte in cagnottes_:
            update_fields = [] # Champs à mettre à jour
            values = [] # Valeurs associées

            # Construction dynamique de la requête SQL selon les champs non nuls

            if cagnotte.name != None:
                update_fields.append("name = %s")
                values.append(cagnotte.name)
            
            if cagnotte.description != None:
                update_fields.append("description = %s")
                values.append(cagnotte.description)
            
            values.append(cagnotte.id_cagnotte)

            query = f"UPDATE Cagnotte_ SET {', '.join(update_fields)} WHERE id = %s;"
            data = tuple(values)
                
            await cursor.execute(query, data)
            
        await conn.commit()

        return RedirectResponse(url="/", status_code=302)
    
    except Exception as e:
        await conn.rollback()

        query = """
        SELECT DISTINCT 
            Cagnotte_.id, Cagnotte_.name, Cagnotte_.description
        
        FROM 
            Cagnotte_
        
        WHERE Cagnotte_.id_user = %s;
    """
        data = (user_data['id_user'])
        
        await cursor.execute(query, data)

        cagnottes = await cursor.fetchall()

        query = """
            SELECT DISTINCT 
                Participant.id, Participant.id_cagnotte, Participant.first_name, Participant.last_name, Participant.amount
            
            FROM 
                Cagnotte_
            
            INNER JOIN
                Participant ON Cagnotte_.id = Participant.id_cagnotte
            
            WHERE Cagnotte_.id_user = %s;
        """
        data = (user_data['id_user'])
        
        await cursor.execute(query, data)

        participants = await cursor.fetchall()

        participants_by_cagnotte = {}

        for participant in participants:
            participants_by_cagnotte.setdefault(participant["id_cagnotte"], []).append(participant)

        # Ajout des participants dans chaque cagnotte
        for cagnotte in cagnottes:
            cagnotte["participants"] = participants_by_cagnotte.get(cagnotte["id"], [])
        
        list_total_amount = await calc_total_amount(cagnottes)

        for cagnotte in cagnottes:
            cagnotte["total_amount"] = list_total_amount.get(cagnotte["id"], [])
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "cagnottes": cagnottes,
            "error": f"Erreur lors de l'ajout {'de la cagnotte' if len(cagnottes_) == 1 else 'des cagnottes'} : {e}"
        })

@router.delete("/cagnotte/del", response_class=HTMLResponse)
async def cagnotte_edit(request: Request, cagnottes_: list[CagnotteDel], conn : aiomysql.Connection = Depends(get_db)):
    token = request.cookies.get("session")
    
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_data = await jwt_required(token, conn)
    except:
        return RedirectResponse(url="/login", status_code=302)

    cursor = await conn.cursor(aiomysql.DictCursor)

    try:
        print(cagnottes_)

        for cagnotte in cagnottes_:
            query = "DELETE FROM Cagnotte_ WHERE id = %s"
            data = (cagnotte.id_cagnotte,)
                
            await cursor.execute(query, data)
            
        await conn.commit()

        return RedirectResponse(url="/", status_code=302)
    
    except Exception as e:
        await conn.rollback()

        query = """
        SELECT DISTINCT 
            Cagnotte_.id, Cagnotte_.name, Cagnotte_.description
        
        FROM 
            Cagnotte_
        
        WHERE Cagnotte_.id_user = %s;
    """
        data = (user_data['id_user'])
        
        await cursor.execute(query, data)

        cagnottes = await cursor.fetchall()

        query = """
            SELECT DISTINCT 
                Participant.id, Participant.id_cagnotte, Participant.first_name, Participant.last_name, Participant.amount
            
            FROM 
                Cagnotte_
            
            INNER JOIN
                Participant ON Cagnotte_.id = Participant.id_cagnotte
            
            WHERE Cagnotte_.id_user = %s;
        """
        data = (user_data['id_user'])
        
        await cursor.execute(query, data)

        participants = await cursor.fetchall()

        participants_by_cagnotte = {}

        for participant in participants:
            participants_by_cagnotte.setdefault(participant["id_cagnotte"], []).append(participant)

        # Ajout des participants dans chaque cagnotte
        for cagnotte in cagnottes:
            cagnotte["participants"] = participants_by_cagnotte.get(cagnotte["id"], [])
        
        list_total_amount = await calc_total_amount(cagnottes)

        for cagnotte in cagnottes:
            cagnotte["total_amount"] = list_total_amount.get(cagnotte["id"], [])
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "cagnottes": cagnottes,
            "error": f"Erreur lors de la suppression {'de la cagnotte' if len(cagnottes_) == 1 else 'des cagnottes'} : {e}"
        })
