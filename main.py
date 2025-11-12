import uuid
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, UUID4
from datetime import date
from typing import Optional

# Initialize the FastAPI app
app = FastAPI(
    title="Employee Management API (Integer emp_id, UUID Internal Keys)",
    description="API using an internal UUID 'id' (API key) and an integer user-assigned 'emp_id' for routing."
)


# Define the Pydantic V2 model for an Employee
class Employee(BaseModel):
    # 'id' is the internal unique database key (UUID/API Key) - server generated
    id: Optional[UUID4] = None

    # 'emp_id' is the user-assigned unique business ID (integer)
    emp_id: int = Field(..., example=101)
    emp_name: str = Field(..., example="Jane Doe")
    city: str = Field(..., example="London")
    country: str = Field(..., example="UK")

    # Field name changed to emp_dob as requested
    emp_dob: date = Field(..., example="1990-01-15")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "emp_id": 101,
                    "emp_name": "Jane Doe",
                    "city": "London",
                    "country": "UK",
                    "emp_dob": "1990-01-15"  # Key updated in example
                }
            ]
        }
    }


# Simple in-memory database:
# Key: internal 'id' (UUID object), Value: Employee object
employees_db: dict[uuid.UUID, Employee] = {}


# --- Helper Functions to Find Employee by Business emp_id ---
def find_employee_by_emp_id_internal(user_emp_id: int) -> Optional[Employee]:
    """Helper to iterate through values and find the matching integer emp_id."""
    for employee in employees_db.values():
        if employee.emp_id == user_emp_id:
            return employee
    return None


def find_employee_key_by_emp_id_internal(user_emp_id: int) -> Optional[uuid.UUID]:
    """Helper to find the internal UUID key for a given integer emp_id."""
    for key, employee in employees_db.items():
        if employee.emp_id == user_emp_id:
            return key
    return None


# --- API Endpoints ---

# Root Endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Employee Management API. Use 'emp_id' in routes like /employees/101"}


# Create Employee (POST)
@app.post("/employees/", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(employee_input: Employee):
    """
    Create a new employee record. The server assigns an internal UUID 'id' (API Key),
    but the client provides the unique business integer 'emp_id'.
    """
    if find_employee_by_emp_id_internal(employee_input.emp_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee business ID '{employee_input.emp_id}' already exists"
        )

    internal_uuid_key = uuid.uuid4()
    employee_to_save = employee_input.model_copy(update={"id": internal_uuid_key})

    employees_db[internal_uuid_key] = employee_to_save
    return employee_to_save


# Read All Employees
@app.get("/employees/", response_model=list[Employee])
def get_all_employees():
    return list(employees_db.values())


# Read Single Employee by emp_id (GET)
@app.get("/employees/{emp_id}", response_model=Employee)
def get_employee_by_emp_id(emp_id: int):
    """Retrieve an employee using their user-assigned integer emp_id."""
    employee = find_employee_by_emp_id_internal(emp_id)
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee with emp_id '{emp_id}' not found")
    return employee


# Update Employee by emp_id (PUT)
@app.put("/employees/{emp_id}", response_model=Employee)
def update_employee_by_emp_id(emp_id: int, updated_details: Employee):
    """
    Updates the entire record for a specific employee using their user-assigned integer emp_id.
    """
    internal_uuid_key = find_employee_key_by_emp_id_internal(emp_id)

    if internal_uuid_key is None:
        raise HTTPException(status_code=404, detail=f"Employee with emp_id '{emp_id}' not found")

    if emp_id != updated_details.emp_id:
        raise HTTPException(status_code=400, detail="Employee business ID in URL must match ID in the request body.")

    # Preserve the *original* internal 'id' (UUID/API key) during the update operation
    employee_to_save = updated_details.model_copy(update={"id": internal_uuid_key})

    employees_db[internal_uuid_key] = employee_to_save
    return employee_to_save


# Delete Employee by emp_id (DELETE)
@app.delete("/employees/{emp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_by_emp_id(emp_id: int):
    """Delete an employee using their user-assigned integer emp_id."""
    internal_uuid_key = find_employee_key_by_emp_id_internal(emp_id)

    if internal_uuid_key is None:
        raise HTTPException(status_code=404, detail=f"Employee with emp_id '{emp_id}' not found")

    del employees_db[internal_uuid_key]
    return f"Employee with emp_id '{emp_id}' deleted successfully."
