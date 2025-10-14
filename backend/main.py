import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # will error at runtime if missing


load_dotenv()
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

app = FastAPI(title="CM Form PD – AI Proxy", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AiRequest(BaseModel):
    prompt: str


class AiResponse(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"ok": True, "model": MODEL}


@app.post("/ai", response_model=AiResponse)
async def ai(req: AiRequest):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY manquant dans l'environnement")
    if OpenAI is None:
        raise HTTPException(status_code=500, detail="Package openai manquant. Installez-le via requirements.txt")

    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Tu es un assistant expert en design de processus et delivery produit."},
                {"role": "user", "content": req.prompt},
            ],
            temperature=0.2,
            max_tokens=900,
        )
        text = (resp.choices[0].message.content or "").strip()
        return AiResponse(text=text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


