from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from routes import auth, dashboard, participant, cagnotte

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.add_middleware(CORSMiddleware, allow_origins=["http://cagnotte.leo-lepinette.fr"])

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.exception_handler(404)
async def not_found(request: Request, exec):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(cagnotte.router)
app.include_router(participant.router)

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080)