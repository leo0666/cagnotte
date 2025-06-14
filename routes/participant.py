from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from aiosmtplib import SMTP
import aiomysql, secrets

from lib.db import get_db
from lib.token import jwt_required
from lib.env import SMTP_USER, SMTP_PWD
from routes.cagnotte import calc_total_amount
from shema.participant_add import ParticipantAdd
from shema.participant_edit import ParticipantEdit
from shema.participant_del import ParticipantDel
from shema.amount_edit import AmountEdit
from shema.participant_access import ParticipantAccess

router = APIRouter()
templates = Jinja2Templates(directory="templates")

async def generate_access_key():
    return secrets.token_urlsafe(64)

async def send_email_access_key(participant, access_url: str):
    smtp_username = SMTP_USER
    smtp_password = SMTP_PWD
    destinataire = participant["email"]

    sujet = "Accès aux cagnottes"
    corps_message = f"""
            Bonjour {participant['first_name']} {participant['last_name']},

            Voici le lien pour accéder au tableau de bord (lecture seule) :
            http://cagnotte.leo-lepinette.fr/view?access_key={access_url}

            Merci de ne pas partager ce lien.

            L'équipe.
            """

    message = MIMEMultipart()
    message["From"] = smtp_username
    message["To"] = destinataire
    message["Subject"] = sujet
    message.attach(MIMEText(corps_message, "plain"))

    try:
        smtp = SMTP(hostname="smtp.gmail.com", port=587, start_tls=True)
        await smtp.connect()
        await smtp.login(smtp_username, smtp_password)
        await smtp.send_message(message)
        await smtp.quit()

        return "Email envoyé"
    except Exception as e:
        return f"Erreur d’envoi : {e}"


@router.post("/participant/add", response_class=HTMLResponse)
async def participants_add(request: Request, participants: list[ParticipantAdd], conn : aiomysql.Connection = Depends(get_db)):
    token = request.cookies.get("session")
    
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        user_data = await jwt_required(token, conn)
    except:
        return RedirectResponse(url="/login", status_code=302)

    cursor = await conn.cursor(aiomysql.DictCursor)

    try:
        for participant in participants:

            query = "INSERT INTO Participant(id_cagnotte, first_name, last_name, email, amount) VALUES (%s, %s, %s, %s, %s)"
            data = (participant.id_cagnotte, participant.first_name, participant.last_name, participant.email, participant.amount)
            
            await cursor.execute(query, data)
        
        await conn.commit()

        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        await conn.rollback()

        query = """
            SELECT DISTINCT 
                Cagnotte_.id, Cagnotte_.name, Cagnotte_.description, Cagnotte_.total_amount
            
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

        participants_ = await cursor.fetchall()

        participants_by_cagnotte = {}

        for participant in participants_:
            participants_by_cagnotte.setdefault(participant["id_cagnotte"], []).append(participant)

        # Ajout des participants dans chaque cagnotte
        for cagnotte in cagnottes:
            cagnotte["participants"] = participants_by_cagnotte.get(cagnotte["id"], [])

            return templates.TemplateResponse("dashboard.html", {
                "request": request,
                "cagnottes": cagnottes,
                "error": f"Erreur lors de l'ajout {'du participant' if len(participants) == 1 else 'des participants'} : {e}"
            })

@router.put("/participant/edit", response_class=HTMLResponse)
async def participant_edit(request: Request, participants: list[ParticipantEdit], conn : aiomysql.Connection = Depends(get_db)):
    token = request.cookies.get("session")
    
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_data = await jwt_required(token, conn)
    except:
        return RedirectResponse(url="/login", status_code=302)

    cursor = await conn.cursor(aiomysql.DictCursor)

    try:

        for participant in participants:
            update_fields = [] # Champs à mettre à jour
            values = [] # Valeurs associées

            # Construction dynamique de la requête SQL selon les champs non nuls

            if participant.first_name != None:
                update_fields.append("first_name = %s")
                values.append(participant.first_name)
            
            if participant.last_name != None:
                update_fields.append("last_name = %s")
                values.append(participant.last_name)

            if participant.email != None:
                update_fields.append("email = %s")
                values.append(participant.email)
            
            if participant.amount != None:
                update_fields.append("amount = %s")
                values.append(participant.amount)
            
            if participant.id_cagnotte != None:
                update_fields.append("id_cagnotte = %s")
                values.append(participant.id_cagnotte)
            
            values.append(participant.id_participant)

            query = f"UPDATE Participant SET {', '.join(update_fields)} WHERE id = %s;"
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
            "error": f"Erreur lors de l'ajout {'de la cagnotte' if len(participants) == 1 else 'des cagnottes'} : {e}"
        })

@router.delete("/participant/del", response_class=HTMLResponse)
async def participant_del(request: Request, participants: list[ParticipantDel], conn : aiomysql.Connection = Depends(get_db)):
    token = request.cookies.get("session")
    
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_data = await jwt_required(token, conn)
    except:
        return RedirectResponse(url="/login", status_code=302)

    cursor = await conn.cursor(aiomysql.DictCursor)

    try:

        for participant in participants:
            query = "DELETE FROM Participant WHERE id = %s"
            data = (participant.id_participant,)
                
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
            "error": f"Erreur lors de la suppression {'de la cagnotte' if len(participants) == 1 else 'des cagnottes'} : {e}"
        })

@router.put("/amount", response_class=HTMLResponse)
async def amount(request: Request, participants: list[AmountEdit], conn : aiomysql.Connection = Depends(get_db)):
    token = request.cookies.get("session")
    
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_data = await jwt_required(token, conn)
    except:
        return RedirectResponse(url="/login", status_code=302)

    cursor = await conn.cursor(aiomysql.DictCursor)

    try:

        for participant in participants:

            query = "UPDATE Participant SET amount = %s WHERE id = %s;"
            data = (participant.amount, participant.id_participant)
                
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
            "error": f"Erreur lors de l'ajout {'de la cagnotte' if len(participants) == 1 else 'des cagnottes'} : {e}"
        })

@router.post("/access_dashboard", response_class=HTMLResponse)
async def access_dashboard(request: Request, participants: list[ParticipantAccess], conn : aiomysql.Connection = Depends(get_db)):
    token = request.cookies.get("session")
    
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_data = await jwt_required(token, conn)
    except:
        return RedirectResponse(url="/login", status_code=302)

    cursor = await conn.cursor(aiomysql.DictCursor)

    try:

        for participant in participants:

            query = "SELECT first_name, last_name, email FROM Participant WHERE id = %s;"
            data = (participant.id_participant)
                
            await cursor.execute(query, data)

            data_participant = await cursor.fetchone()

            access_key = await generate_access_key()

            query = "UPDATE Participant SET access_key = %s WHERE id = %s;"
            data = (access_key, participant.id_participant)

            await cursor.execute(query, data)

            await conn.commit()

            await send_email_access_key(data_participant, access_key)

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
            "error": f"Erreur lors de l'ajout {'de la cagnotte' if len(participants) == 1 else 'des cagnottes'} : {e}"
        })

