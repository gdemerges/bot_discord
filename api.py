from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import uvicorn
import os

OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")

openai.api_key = OPENAI_API_KEY

app = FastAPI()

class RequestBody(BaseModel):
    text: str
    
@app.get("/")
def read_root():
    return {"message": "API en ligne"}

@app.post("/analyze")
async def analyze_text(request: RequestBody):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": request.text}]
        )
        return {"response": response["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)