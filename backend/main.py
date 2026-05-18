from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Optional
import calendar

import models
import schemas
import auth
from database import engine, get_db, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="勤怠管理システム", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_default_users(db: Session):
    """Create default users if they don't exist."""
    default_users = [
        {
            "username": "admin",
            "password": "admin123",
            "full_name": "システム管理者",
            "role": "admin",
        },
        {
            "username": "employee1",
            "password": "emp123",
            "full_name": "田中 太郎",
            "role": "employee",
        },
        {
            "username": "employee2",
            "password": "emp123",
            "full_name": "鈴木 花子",
            "role": "employee",
        },
    ]
    for user_data in default_users:
        existing = db.query(models.User).filter(models.User.username == user_data["username"]).first()
        if not existing:
            user = models.User(
                username=user_data["username"],
                password_hash=auth.hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
            )
            db.add(user)
    db.commit()


@app.on_event("startup")
def startup_event():
    db = next(get_db())
    try:
        seed_default_users(db)
    finally:
        db.close()


# ── Auth endpoints ──────────────────────────────────────────────────────────

@app.post("/api/auth/login", response_model=schemas.TokenResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user or not auth.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
        )
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return schemas.TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserResponse.model_validate(user),
    )


@app.get("/api/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# ── Attendance endpoints ────────────────────────────────────────────────────

@app.post("/api/attendance/clock-in", response_model=schemas.AttendanceResponse)
def clock_in(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    existing = db.query(models.Attendance).filter(
        models.Attendance.user_id == current_user.id,
        models.Attendance.date == today,
    ).first()
    if existing:
        if existing.clock_in is not None:
            raise HTTPException(status_code=400, detail="本日はすでに出勤打刻済みです")
        existing.clock_in = datetime.now()
        db.commit()
        db.refresh(existing)
        return existing
    record = models.Attendance(
        user_id=current_user.id,
        clock_in=datetime.now(),
        date=today,
        work_minutes=0,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.post("/api/attendance/clock-out", response_model=schemas.AttendanceResponse)
def clock_out(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    record = db.query(models.Attendance).filter(
        models.Attendance.user_id == current_user.id,
        models.Attendance.date == today,
    ).first()
    if not record or record.clock_in is None:
        raise HTTPException(status_code=400, detail="出勤打刻がありません")
    if record.clock_out is not None:
        raise HTTPException(status_code=400, detail="本日はすでに退勤打刻済みです")
    now = datetime.now()
    record.clock_out = now
    delta = now - record.clock_in
    record.work_minutes = int(delta.total_seconds() / 60)
    db.commit()
    db.refresh(record)
    return record


@app.get("/api/attendance/today", response_model=Optional[schemas.AttendanceResponse])
def get_today_attendance(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    record = db.query(models.Attendance).filter(
        models.Attendance.user_id == current_user.id,
        models.Attendance.date == today,
    ).first()
    return record


@app.get("/api/attendance/summary", response_model=schemas.MonthlySummaryResponse)
def get_monthly_summary(
    month: str,  # format: YYYY-MM
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    try:
        year, mon = map(int, month.split("-"))
        start_date = date(year, mon, 1)
        last_day = calendar.monthrange(year, mon)[1]
        end_date = date(year, mon, last_day)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="月の形式が正しくありません (YYYY-MM)")

    records = db.query(models.Attendance).filter(
        models.Attendance.user_id == current_user.id,
        models.Attendance.date >= start_date,
        models.Attendance.date <= end_date,
    ).order_by(models.Attendance.date).all()

    total_work_minutes = sum(r.work_minutes or 0 for r in records)
    work_days = len([r for r in records if r.clock_in is not None])

    summary_items = [
        schemas.AttendanceSummaryItem(
            date=r.date,
            clock_in=r.clock_in,
            clock_out=r.clock_out,
            work_minutes=r.work_minutes or 0,
        )
        for r in records
    ]

    return schemas.MonthlySummaryResponse(
        month=month,
        total_work_minutes=total_work_minutes,
        work_days=work_days,
        records=summary_items,
    )


# ── Leave request endpoints ────────────────────────────────────────────────

@app.post("/api/leave/request", response_model=schemas.LeaveRequestResponse)
def create_leave_request(
    request: schemas.LeaveRequestCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if request.end_date < request.start_date:
        raise HTTPException(status_code=400, detail="終了日は開始日以降にしてください")
    leave = models.LeaveRequest(
        user_id=current_user.id,
        start_date=request.start_date,
        end_date=request.end_date,
        reason=request.reason,
        status="pending",
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave


@app.get("/api/leave/my-requests", response_model=List[schemas.LeaveRequestResponse])
def get_my_leave_requests(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    requests = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.user_id == current_user.id
    ).order_by(models.LeaveRequest.created_at.desc()).all()
    return requests


# ── Admin endpoints ────────────────────────────────────────────────────────

@app.get("/api/admin/attendance", response_model=List[schemas.AdminAttendanceItem])
def get_all_attendance(
    target_date: Optional[str] = None,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db),
):
    if target_date:
        try:
            query_date = date.fromisoformat(target_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="日付の形式が正しくありません")
    else:
        query_date = date.today()

    records = (
        db.query(models.Attendance, models.User)
        .join(models.User, models.Attendance.user_id == models.User.id)
        .filter(models.Attendance.date == query_date)
        .all()
    )

    # Also include users who have no record today
    users_with_records = {r.user_id for r, _ in records}
    all_employees = db.query(models.User).filter(models.User.role == "employee").all()

    result = []
    for attendance, user in records:
        result.append(
            schemas.AdminAttendanceItem(
                user_id=user.id,
                username=user.username,
                full_name=user.full_name,
                date=attendance.date,
                clock_in=attendance.clock_in,
                clock_out=attendance.clock_out,
                work_minutes=attendance.work_minutes or 0,
            )
        )

    for employee in all_employees:
        if employee.id not in users_with_records:
            result.append(
                schemas.AdminAttendanceItem(
                    user_id=employee.id,
                    username=employee.username,
                    full_name=employee.full_name,
                    date=query_date,
                    clock_in=None,
                    clock_out=None,
                    work_minutes=0,
                )
            )

    return result


@app.get("/api/admin/leave-requests", response_model=List[schemas.LeaveRequestResponse])
def get_all_leave_requests(
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db),
):
    requests = (
        db.query(models.LeaveRequest)
        .join(models.User, models.LeaveRequest.user_id == models.User.id)
        .order_by(models.LeaveRequest.created_at.desc())
        .all()
    )
    return requests


@app.put("/api/admin/leave-requests/{request_id}", response_model=schemas.LeaveRequestResponse)
def update_leave_request(
    request_id: int,
    update: schemas.LeaveRequestUpdate,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db),
):
    if update.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="ステータスは approved または rejected にしてください")
    leave = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == request_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="休暇申請が見つかりません")
    leave.status = update.status
    db.commit()
    db.refresh(leave)
    return leave


@app.post("/api/admin/users", response_model=schemas.UserResponse)
def create_user(
    user_data: schemas.UserCreate,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db),
):
    existing = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="そのユーザー名はすでに使用されています")
    user = models.User(
        username=user_data.username,
        password_hash=auth.hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
