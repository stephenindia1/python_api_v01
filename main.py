from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import date
from typing import Dict

# Initialize the FastAPI application
app = FastAPI(
    title="Employee API",
    description="An API to manage employee records"
)

# Pydantic model for the employee data structure
class Employee(BaseModel):
    emp_id: int
    emp_name: str
    city: str
    country: str
    emp_dob: date

# A simple in-memory database (dictionary) to store employees
# In a real application, you would use a database like PostgreSQL or MongoDB
db: Dict[int, Employee] = {}

@app.post("/employees/", response_model=Employee, status_code=201)
def create_employee(employee: Employee):
    """
    Create a new employee record.
    """
    if employee.emp_id in db:
        raise HTTPException(status_code=400, detail="Employee with this ID already exists")
    db[employee.emp_id] = employee
    return employee

@app.get("/employees/{emp_id}", response_model=Employee)
def read_employee(emp_id: int):
    """
    Retrieve an employee record by their ID.
    """
    if emp_id not in db:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db[emp_id]

@app.get("/employees/", response_model=Dict[int, Employee])
def list_employees():
    """
    List all employee records.
    """
    return db
