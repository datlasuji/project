from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import create_database, get_connection

app = FastAPI(title="Motor Insurance Claim Estimator")

# Create database
create_database()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Request Model
# =========================

class ClaimRequest(BaseModel):
    vehicle_age: int
    model_id: int
    part_ids: list[int]
    labour: float
    deductible: float
    amount_claimed: float
    available_amount: float


# =========================
# Depreciation
# =========================

def get_depreciation_rate(
    part_type: str,
    vehicle_age: int
) -> float:

    if part_type == "Metal":
        rate = 0.05 * vehicle_age

    elif part_type == "Rubber":
        rate = 0.03 * vehicle_age

    elif part_type == "Glass":
        rate = 0.02 * vehicle_age

    else:
        rate = 0.00

    return min(rate, 0.50)


# =========================
# Home
# =========================

@app.get("/")
def home():
    return {
        "message": "Motor Insurance Claim Estimator API is running"
    }


# =========================
# Get Vehicle Models
# =========================

@app.get("/api/vehicles")
def get_vehicles():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM vehicle_models
        ORDER BY brand, model
    """)

    vehicles = cursor.fetchall()
    connection.close()

    return [dict(vehicle) for vehicle in vehicles]


# =========================
# Get Parts For Model
# =========================

@app.get("/api/parts")
def get_parts(model_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM parts
        WHERE model_id = ?
        ORDER BY name
    """, (model_id,))

    parts = cursor.fetchall()
    connection.close()

    return [dict(part) for part in parts]


# =========================
# Calculate Claim
# =========================

@app.post("/api/claim/calculate")
def calculate_claim(request: ClaimRequest):

    connection = get_connection()
    cursor = connection.cursor()

    # -------------------------
    # Get selected parts
    # -------------------------

    placeholders = ",".join(
        ["?"] * len(request.part_ids)
    )

    cursor.execute(
        f"""
        SELECT *
        FROM parts
        WHERE model_id = ?
        AND id IN ({placeholders})
        """,
        [request.model_id] + request.part_ids
    )

    parts = cursor.fetchall()
    connection.close()

    # -------------------------
    # Calculate parts
    # -------------------------

    parts_cost = 0
    total_depreciation = 0
    part_details = []

    for part in parts:

        price = float(part["price"])
        part_type = part["type"]

        depreciation_rate = get_depreciation_rate(
            part_type,
            request.vehicle_age
        )

        depreciation_amount = (
            price * depreciation_rate
        )

        parts_cost += price
        total_depreciation += depreciation_amount

        part_details.append({
            "name": part["name"],
            "type": part_type,
            "price": round(price, 2),
            "depreciation_rate": round(
                depreciation_rate * 100,
                2
            ),
            "depreciation_amount": round(
                depreciation_amount,
                2
            )
        })

    # -------------------------
    # Gross Repair Cost
    # -------------------------

    gross_repair_cost = (
        parts_cost + request.labour
    )

    # -------------------------
    # After Depreciation
    # -------------------------

    amount_after_depreciation = (
        gross_repair_cost
        - total_depreciation
    )

    # -------------------------
    # After Deductible
    # -------------------------

    claim_after_deductible = max(
        amount_after_depreciation
        - request.deductible,
        0
    )

    # -------------------------
    # Final Claim
    # -------------------------
    #
    # Claim cannot be more than:
    # 1. Amount claimed
    # 2. Available insurance amount
    # 3. Eligible claim after deductible
    #

    final_claim = min(
        claim_after_deductible,
        request.amount_claimed,
        request.available_amount
    )

    # -------------------------
    # Return Result
    # -------------------------

    return {

        "vehicle_age": request.vehicle_age,

        "parts": part_details,

        "parts_cost": round(
            parts_cost,
            2
        ),

        "labour": round(
            request.labour,
            2
        ),

        "gross_repair_cost": round(
            gross_repair_cost,
            2
        ),

        "total_depreciation": round(
            total_depreciation,
            2
        ),

        "amount_after_depreciation": round(
            amount_after_depreciation,
            2
        ),

        "amount_claimed": round(
            request.amount_claimed,
            2
        ),

        "available_amount": round(
            request.available_amount,
            2
        ),

        "voluntary_deductible": round(
            request.deductible,
            2
        ),

        "claim_after_deductible": round(
            claim_after_deductible,
            2
        ),

        "final_estimated_claim": round(
            final_claim,
            2
        )
    }