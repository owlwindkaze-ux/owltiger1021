import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach JWT token from localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// ── Type definitions ──────────────────────────────────────────────────────

export interface User {
  id: number
  username: string
  full_name: string
  role: string
  created_at: string
}

export interface AttendanceRecord {
  id: number
  user_id: number
  clock_in: string | null
  clock_out: string | null
  date: string
  work_minutes: number
}

export interface AttendanceSummaryItem {
  date: string
  clock_in: string | null
  clock_out: string | null
  work_minutes: number
}

export interface MonthlySummary {
  month: string
  total_work_minutes: number
  work_days: number
  records: AttendanceSummaryItem[]
}

export interface LeaveRequest {
  id: number
  user_id: number
  start_date: string
  end_date: string
  reason: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  user?: User
}

export interface AdminAttendanceItem {
  user_id: number
  username: string
  full_name: string
  date: string
  clock_in: string | null
  clock_out: string | null
  work_minutes: number
}

// ── API functions ─────────────────────────────────────────────────────────

export const authApi = {
  login: (username: string, password: string) =>
    api.post<{ access_token: string; token_type: string; user: User }>('/api/auth/login', { username, password }),
  me: () => api.get<User>('/api/auth/me'),
}

export const attendanceApi = {
  clockIn: () => api.post<AttendanceRecord>('/api/attendance/clock-in'),
  clockOut: () => api.post<AttendanceRecord>('/api/attendance/clock-out'),
  today: () => api.get<AttendanceRecord | null>('/api/attendance/today'),
  summary: (month: string) => api.get<MonthlySummary>(`/api/attendance/summary?month=${month}`),
}

export const leaveApi = {
  request: (data: { start_date: string; end_date: string; reason: string }) =>
    api.post<LeaveRequest>('/api/leave/request', data),
  myRequests: () => api.get<LeaveRequest[]>('/api/leave/my-requests'),
}

export const adminApi = {
  attendance: (targetDate?: string) =>
    api.get<AdminAttendanceItem[]>(`/api/admin/attendance${targetDate ? `?target_date=${targetDate}` : ''}`),
  leaveRequests: () => api.get<LeaveRequest[]>('/api/admin/leave-requests'),
  updateLeaveRequest: (id: number, status: string) =>
    api.put<LeaveRequest>(`/api/admin/leave-requests/${id}`, { status }),
  createUser: (data: { username: string; password: string; full_name: string; role: string }) =>
    api.post<User>('/api/admin/users', data),
}
