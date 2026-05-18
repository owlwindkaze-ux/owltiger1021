import React, { useState, useEffect } from 'react'
import { attendanceApi, AttendanceRecord } from '../api'

function formatTime(isoString: string | null): string {
  if (!isoString) return '--:--'
  return new Date(isoString).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
}

function formatMinutes(minutes: number): string {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return `${h}時間${m}分`
}

export default function AttendanceClock() {
  const [now, setNow] = useState(new Date())
  const [record, setRecord] = useState<AttendanceRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null)

  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    attendanceApi.today()
      .then(res => setRecord(res.data))
      .catch(() => setRecord(null))
      .finally(() => setLoading(false))
  }, [])

  const showMessage = (text: string, type: 'success' | 'error') => {
    setMessage({ text, type })
    setTimeout(() => setMessage(null), 3000)
  }

  const handleClockIn = async () => {
    setActionLoading(true)
    try {
      const res = await attendanceApi.clockIn()
      setRecord(res.data)
      showMessage('出勤打刻が完了しました', 'success')
    } catch (err: any) {
      showMessage(err.response?.data?.detail || '打刻に失敗しました', 'error')
    } finally {
      setActionLoading(false)
    }
  }

  const handleClockOut = async () => {
    setActionLoading(true)
    try {
      const res = await attendanceApi.clockOut()
      setRecord(res.data)
      showMessage('退勤打刻が完了しました', 'success')
    } catch (err: any) {
      showMessage(err.response?.data?.detail || '打刻に失敗しました', 'error')
    } finally {
      setActionLoading(false)
    }
  }

  const cardStyle: React.CSSProperties = {
    backgroundColor: '#fff',
    borderRadius: '12px',
    padding: '32px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
    marginBottom: '24px',
  }

  const clockStyle: React.CSSProperties = {
    fontSize: '52px',
    fontWeight: 700,
    color: '#1a237e',
    textAlign: 'center',
    letterSpacing: '2px',
    marginBottom: '4px',
  }

  const dateStyle: React.CSSProperties = {
    textAlign: 'center',
    color: '#666',
    fontSize: '14px',
    marginBottom: '28px',
  }

  const statusRowStyle: React.CSSProperties = {
    display: 'flex',
    gap: '16px',
    marginBottom: '24px',
  }

  const statusItemStyle: React.CSSProperties = {
    flex: 1,
    backgroundColor: '#f5f7ff',
    borderRadius: '8px',
    padding: '16px',
    textAlign: 'center',
  }

  const btnStyle = (color: string, disabled: boolean): React.CSSProperties => ({
    flex: 1,
    padding: '14px',
    backgroundColor: disabled ? '#e0e0e0' : color,
    color: disabled ? '#9e9e9e' : '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 600,
    cursor: disabled ? 'not-allowed' : 'pointer',
  })

  const canClockIn = !record?.clock_in
  const canClockOut = !!record?.clock_in && !record?.clock_out

  return (
    <div style={cardStyle}>
      <div style={clockStyle}>
        {now.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
      </div>
      <div style={dateStyle}>
        {now.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })}
      </div>

      {!loading && (
        <>
          <div style={statusRowStyle}>
            <div style={statusItemStyle}>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>出勤時刻</div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: record?.clock_in ? '#1a237e' : '#bdbdbd' }}>
                {formatTime(record?.clock_in ?? null)}
              </div>
            </div>
            <div style={statusItemStyle}>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>退勤時刻</div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: record?.clock_out ? '#1a237e' : '#bdbdbd' }}>
                {formatTime(record?.clock_out ?? null)}
              </div>
            </div>
            <div style={statusItemStyle}>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>勤務時間</div>
              <div style={{ fontSize: '18px', fontWeight: 700, color: '#1a237e' }}>
                {record?.work_minutes ? formatMinutes(record.work_minutes) : '--'}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={handleClockIn}
              disabled={!canClockIn || actionLoading}
              style={btnStyle('#2e7d32', !canClockIn || actionLoading)}
            >
              出勤
            </button>
            <button
              onClick={handleClockOut}
              disabled={!canClockOut || actionLoading}
              style={btnStyle('#c62828', !canClockOut || actionLoading)}
            >
              退勤
            </button>
          </div>

          {message && (
            <div style={{
              marginTop: '16px',
              padding: '10px 14px',
              borderRadius: '8px',
              fontSize: '14px',
              backgroundColor: message.type === 'success' ? '#e8f5e9' : '#ffebee',
              color: message.type === 'success' ? '#2e7d32' : '#c62828',
            }}>
              {message.text}
            </div>
          )}
        </>
      )}
    </div>
  )
}
