from fastapi import Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
import datetime, aiomysql, jwt

from lib.db import get_db
from lib.env import JWT_SECRET, JWT_ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def create_jwt_token(data: dict, expires_in: datetime.timedelta):
    to_encode = data.copy() # Copie des données à encoder
    expire = datetime.datetime.utcnow() + expires_in 
    to_encode.update({"expire": expire.isoformat()})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM), expire

# Dépendance FastAPI utilisée pour sécuriser les routes
# Vérifie que le token JWT passé dans les headers est valide et non expiré
async def jwt_required(token: str = Depends(oauth2_scheme), conn : aiomysql.Connection = Depends(get_db)):

    cursor = await conn.cursor(aiomysql.DictCursor)

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        query_access_token = "SELECT id_user, expire_access_token FROM Token WHERE access_token = %s"
        data_access_token = (token,)

        await cursor.execute(query_access_token, data_access_token)
                
        result = await cursor.fetchone()

        if not result:
            raise HTTPException(status_code=498, detail="Token invalide")

        expire_access_token = result["expire_access_token"]

        if expire_access_token <= datetime.datetime.utcnow():
            raise HTTPException(status_code=498, detail="Token expiré")

        return payload # Renvoie les données décodées du token si tout est bon

    except jwt.ExpiredSignatureError: # Cas où le token a expiré (signature JWT)
        raise HTTPException(status_code=498, detail="Token expiré")
    except jwt.InvalidTokenError: # Cas où le token est mal formé ou incorrect
        raise HTTPException(status_code=498, detail="Token invalide")

# Vérifie et rafraîchit un access token
async def jwt_required_refresh(request: Request, conn : aiomysql.Connection = Depends(get_db)):

    cursor = await conn.cursor(aiomysql.DictCursor)

    token = request.headers.get("Authorization") # Récupère le header Authorization

    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=498, detail="Refresh token manquant ou invalide")

    try:
        token = token.split(" ")[1] # Extrait le token brut sans le "Bearer"
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Récupère les infos utiles dans un dictionnaire
        dict_user = {"nom_prenom" : payload["nom_prenom"], "id_ferme" : payload['id_ferme'], "nom_role" : payload['nom_role']}

        query = "SELECT id_personne, expire_refresh_token FROM Token WHERE refresh_token = %s"
        data = (token,)

        await cursor.execute(query, data)
                
        response = await cursor.fetchone()

        if not response:
            raise HTTPException(status_code=498, detail="Refresh token invalide ou expiré")

        # user_id = user["id_personne"]
        
        expire_access_token = response["expire_refresh_token"]

        if expire_access_token <= datetime.datetime.utcnow():
            raise HTTPException(status_code=498, detail="Refresh token expiré")

        return dict_user, token # Retourne les infos de l’utilisateur et le token

    except jwt.ExpiredSignatureError: # Cas où le token a expiré (signature JWT)
        raise HTTPException(status_code=498, detail="Refresh token expiré")
    except jwt.InvalidTokenError: # Cas où le token est mal formé ou incorrect
        raise HTTPException(status_code=498, detail="Refresh token invalide")

