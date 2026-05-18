from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# Auth schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: "UserResponse"


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "employee"


# Attendance schemas
class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    clock_in: Optional[datetime]
    clock_out: Optional[datetime]
    date: date
    work_minutes: int

    model_config = {"from_attributes": True}


class AttendanceSummaryItem(BaseModel):
    date: date
    clock_in: Optional[datetime]
    clock_out: Optional[datetime]
    work_minutes: int

    model_config = {"from_attributes": True}


class MonthlySummaryResponse(BaseModel):
    month: str
    total_work_minutes: int
    work_days: int
    records: List[AttendanceSummaryItem]


class AdminAttendanceItem(BaseModel):
    user_id: int
    username: str
    full_name: str
    date: date
    clock_in: Optional[datetime]
    clock_out: Optional[datetime]
    work_minutes: int

    model_config = {"from_attributes": True}


# Leave request schemas
class LeaveRequestCreate(BaseModel):
    start_date: date
    end_date: date
    reason: str


class LeaveRequestResponse(BaseModel):
    id: int
    user_id: int
    start_date: date
    end_date: date
    reason: str
    status: str
    created_at: datetime
    user: Optional[UserResponse] = None

    model_config = {"from_attributes": True}


class LeaveRequestUpdate(BaseModel):
    status: str  # approved or rejected


TokenResponse.model_rebuild()
