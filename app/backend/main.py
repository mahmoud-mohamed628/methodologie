import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.schemas import PredictionResponse
from backend.predictor import predictor

BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()

# Mount frontend and serve index.html at /frontend
app.mount(
    "/frontend",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend",
)


@app.get("/")
def read_root():
    return {"message": "Colon Cancer Prediction API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/genes")
def get_genes():
    if not predictor.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé. Lancez d'abord le service training."
        )
    return {"selected_genes": predictor.get_genes()}


@app.post("/predict", response_model=PredictionResponse)
def predict(data: dict):
    if not predictor.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé. Lancez d'abord le service training."
        )

    try:
        prediction, confidence = predictor.predict(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PredictionResponse(
        prediction=prediction,
        confidence=confidence
    )
