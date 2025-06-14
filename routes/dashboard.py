from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import aiomysql

from lib.db import get_db
from lib.token import jwt_required
from routes.cagnotte import calc_total_amount

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, conn : aiomysql.Connection = Depends(get_db)):
    token = request.cookies.get("session")
    
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_data = await jwt_required(token, conn)
    except:
        return RedirectResponse(url="/login", status_code=302)

    cursor = await conn.cursor(aiomysql.DictCursor)

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
        "cagnottes": cagnottes
    })

@router.get("/view", response_class=HTMLResponse)
async def dashboard(request: Request, access_key: str, conn : aiomysql.Connection = Depends(get_db)):

    cursor = await conn.cursor(aiomysql.DictCursor)

    query = "SELECT id FROM Participant WHERE access_key = %s"
    data = (access_key,)

    await cursor.execute(query, data)
    
    participant = await cursor.fetchone()

    if not participant:
        raise templates.TemplateResponse("404.html", {
        "request": request,
    })

    query = """
        SELECT DISTINCT 
            Cagnotte_.id, Cagnotte_.name, Cagnotte_.description
        
        FROM 
            Cagnotte_
        
        INNER JOIN
            Participant ON Cagnotte_.id = Participant.id_cagnotte
        
        WHERE
            Participant.id = %s;
    """
    data = (participant['id'])
    
    await cursor.execute(query, data)

    cagnottes = await cursor.fetchall()

    query = """
        SELECT DISTINCT 
            Participant.id, Participant.id_cagnotte, Participant.first_name, Participant.last_name, Participant.amount
        
        FROM 
            Cagnotte_
        
        INNER JOIN
            Participant ON Cagnotte_.id = Participant.id_cagnotte
        
        WHERE Participant.id = %s;
    """
    data = (participant['id'])
    
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
    
    return templates.TemplateResponse("read-only_dashboard.html", {
        "request": request,
        "cagnottes": cagnottes
    })
