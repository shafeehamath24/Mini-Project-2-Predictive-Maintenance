
# Stage 19 — Create the Cloud Engineering

from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# Step 4 — Allow the frontend to communicate with FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import FileResponse

# Create the FastAPI application
app = FastAPI(title="Predictive Maintenance API")

# Allow the local frontend to send requests to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501"
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)

# Step 1 — Set the project paths
BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"

MODEL_PATH = BASE_DIR / "backend" / "failure_model.pkl"
DATA_PATH = BASE_DIR / "ai4i2020.csv"

# Step 2 — Load the trained AI model and its feature names
# saved = joblib.load(MODEL_PATH)
# model = saved["model"]
# features = saved["features"]


saved = joblib.load(MODEL_PATH)
model = saved["model"]
features = saved["features"]
threshold = saved.get("threshold", 0.50)


# Step 3 — Load the AI4I 2020 historical machine dataset
machines = pd.read_csv(DATA_PATH)


# Step 4 — Validate the machine sensor values received from the frontend
class MachineData(BaseModel):
    machine_type: str = Field(pattern="^(L|M|H)$")
    air_temperature: float = Field(ge=250, le=400)
    process_temperature: float = Field(ge=250, le=450)
    rotational_speed: int = Field(gt=0, le=10000)
    torque: float = Field(ge=0, le=1000)
    tool_wear: int = Field(ge=0, le=1000)


# Cloud Engineering — Check whether the API is running
# @app.get("/")
# def home():
#     return {
#         "project": "Predictive Maintenance for Smart Manufacturing",
#         "status": "running",
#         "module": "Cloud Engineering"
#     }

@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/style.css")
def get_stylesheet():
    return FileResponse(FRONTEND_DIR / "style.css")


@app.get("/script.js")
def get_script():
    return FileResponse(FRONTEND_DIR / "script.js")


@app.get("/api/status")
def project_status():
    return {
        "project": "Predictive Maintenance for Smart Manufacturing",
        "status": "running",
        "module": "Cloud Engineering"
    }


# Security Engineering — Check backend and model availability
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": True,
        "dataset_loaded": True,
        "dataset_records": len(machines)
    }


# Data Engineering — Return historical records from the CSV dataset
# Limit the number of records returned in a single request

@app.get("/machines")
def get_machines(offset: int = 0, limit: int = 5, failure_only: bool = False):
    # Load the original AI4I dataset
    machines = pd.read_csv(BASE_DIR / "ai4i2020.csv")

    # Optionally select only records where a machine failure occurred
    if failure_only:
        machines = machines[machines["Machine failure"] == 1]

    # Calculate the total records after applying the filter
    total_records = len(machines)

    # Keep pagination values within safe limits
    offset = max(0, offset)
    limit = max(1, min(limit, 100))

    # Select the requested records
    records = machines.iloc[offset:offset + limit].copy()

    # Convert missing values into JSON-compatible null values
    records = records.astype(object).where(pd.notna(records), None)

    # Return the records as JSON
    return {
        "total_records": total_records,
        "returned_records": len(records),
        "offset": offset,
        "machines": records.to_dict(orient="records")
    }



# Data Engineering — Retrieve one machine using its UDI
@app.get("/machines/{udi}")
def get_machine(udi: int):
    record = machines[machines["UDI"] == udi]

    # Return an error if the requested machine does not exist
    if record.empty:
        raise HTTPException(
            status_code=404,
            detail="Machine record not found"
        )

    # Convert the selected CSV row into a JSON response
    return record.iloc[0].to_dict()


# AI Engineering — Predict whether a machine is likely to fail
@app.post("/predict")
def predict(data: MachineData):

    # Convert the received sensor values into model input features
    row = {
        "Air temperature [K]": data.air_temperature,
        "Process temperature [K]": data.process_temperature,
        "Rotational speed [rpm]": data.rotational_speed,
        "Torque [Nm]": data.torque,
        "Tool wear [min]": data.tool_wear,
        "Type_L": int(data.machine_type == "L"),
        "Type_M": int(data.machine_type == "M"),
        "Type_H": int(data.machine_type == "H")
    }

    # Arrange the input columns in the same order used during training
    frame = pd.DataFrame([row]).reindex(
        columns=features,
        fill_value=0
    )

    # Generate the prediction and estimated failure probability

    # prediction = int(model.predict(frame)[0])
    # probability = float(model.predict_proba(frame)[0][1])

    # probability = float(model.predict_proba(frame)[0][1])
    # prediction = int(probability >= threshold)


    probability = float(model.predict_proba(frame)[0][1])
    threshold = 0.30
    prediction = int(probability >= threshold)
    

    # Send the prediction result back to the frontend
    return {
        "machine_type": data.machine_type,
        "failure_prediction": prediction,
        "failure_label": (
            "Failure risk detected"
            if prediction == 1
            else "No failure predicted"
        ),
        "failure_probability": round(probability, 4)
    }
