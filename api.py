from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import json

with open('data/config.json', 'r') as f:
    config = json.load(f)

client = OpenAI(api_key=config.get("OPENAI_API_KEY"))

app = FastAPI()

class RequestBody(BaseModel):
    text: str

@app.post("/analyze")
async def analyze_text(request: RequestBody):
    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[{"role": "user", "content": request.text}])
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))