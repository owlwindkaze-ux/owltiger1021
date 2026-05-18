import React, { useState, useEffect } from 'react'
import { adminApi, AdminAttendanceItem, LeaveRequest } from '../api'

const STATUS_LABEL: Record<string, { label: string; bg: string; color: string }> = {
  pending:  { label: '審査中', bg: '#fff9c4', color: '#f57f17' },
  approved: { label: '承認済', bg: '#e8f5e9', color: '#2e7d32' },
  rejected: { label: '却下',   bg: '#ffebee', color: '#c62828' },
}

function formatTime(iso: string | null): string {
  if (!iso) return '--:--'
  return new Date(iso).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
}

function formatMinutes(minutes: number): string {
  if (!minutes) return '--'
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return `${h}h${String(m).padStart(2, '0')}m`
}

export default function AdminDashboard() {
  const [tab, setTab] = useState<'attendance' | 'leave'>('attendance')
  const [attendance, setAttendance] = useState<AdminAttendanceItem[]>([])
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([])
  const [loadingA, setLoadingA] = useState(true)
  const [loadingL, setLoadingL] = useState(true)
  const [actionMsg, setActionMsg] = useState<{ text: string; type: 'success' | 'error' } | null>(null)

  useEffect(() => {
    setLoadingA(true)
    adminApi.attendance()
      .then(res => setAttendance(res.data))
      .catch(() => setAttendance([]))
      .finally(() => setLoadingA(false))

    setLoadingL(true)
    adminApi.leaveRequests()
      .then(res => setLeaveRequests(res.data))
      .catch(() => setLeaveRequests([]))
      .finally(() => setLoadingL(false))
  }, [])

  const handleLeaveAction = async (id: number, status: 'approved' | 'rejected') => {
    try {
      const res = await adminApi.updateLeaveRequest(id, status)
      setLeaveRequests(prev => prev.map(r => r.id === id ? res.data : r))
      setActionMsg({ text: status === 'approved' ? '承認しました' : '却下しました', type: 'success' })
      setTimeout(() => setActionMsg(null), 3000)
    } catch {
      setActionMsg({ text: '操作に失敗しました', type: 'error' })
      setTimeout(() => setActionMsg(null), 3000)
    }
  }

  const cardStyle: React.CSSProperties = {
    backgroundColor: '#fff',
    borderRadius: '12px',
    padding: '24px 32px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
  }

  const tabStyle = (active: boolean): React.CSSProperties => ({
    padding: '10px 24px',
    border: 'none',
    borderBottom: active ? '3px solid #1a237e' : '3px solid transparent',
    backgroundColor: 'transparent',
    color: active ? '#1a237e' : '#666',
    fontWeight: active ? 700 : 400,
    fontSize: '15px',
    cursor: 'pointer',
  })

  const thStyle: React.CSSProperties = {
    padding: '10px 12px',
    textAlign: 'left',
    fontSize: '13px',
    color: '#666',
    fontWeight: 600,
    borderBottom: '2px solid #e0e0e0',
  }

  const tdStyle: React.CSSProperties = {
    padding: '10px 12px',
    fontSize: '14px',
    borderBottom: '1px solid #f0f0f0',
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1000px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '22px', fontWeight: 700, color: '#333', marginBottom: '24px' }}>管理者ダッシュボード</h2>

      {actionMsg && (
        <div style={{
          padding: '12px 16px',
          borderRadius: '8px',
          marginBottom: '16px',
          backgroundColor: actionMsg.type === 'success' ? '#e8f5e9' : '#ffebee',
          color: actionMsg.type === 'success' ? '#2e7d32' : '#c62828',
          fontSize: '14px',
        }}>
          {actionMsg.text}
        </div>
      )}

      <div style={{ borderBottom: '1px solid #e0e0e0', marginBottom: '24px' }}>
        <button style={tabStyle(tab === 'attendance')} onClick={() => setTab('attendance')}>
          今日の出勤状況
        </button>
        <button style={tabStyle(tab === 'leave')} onClick={() => setTab('leave')}>
          休暇申請一覧
        </button>
      </div>

      <div style={cardStyle}>
        {tab === 'attendance' && (
          <>
            <h3 style={{ margin: '0 0 20px', fontSize: '16px', color: '#1a237e' }}>
              {new Date().toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' })} の出勤状況
            </h3>
            {loadingA ? (
              <div style={{ textAlign: 'center', padding: '32px', color: '#666' }}>読み込み中...</div>
            ) : attendance.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '32px', color: '#999' }}>従業員データがありません</div>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    {['氏名', 'ユーザー名', '出勤', '退勤', '勤務時間', 'ステータス'].map(h => (
                      <th key={h} style={thStyle}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {attendance.map(a => {
                    const isWorking = !!a.clock_in && !a.clock_out
                    const isDone = !!a.clock_in && !!a.clock_out
                    return (
                      <tr key={a.user_id} style={{ backgroundColor: isWorking ? '#fffde7' : '#fff' }}>
                        <td style={{ ...tdStyle, fontWeight: 600 }}>{a.full_name}</td>
                        <td style={{ ...tdStyle, color: '#888' }}>{a.username}</td>
                        <td style={tdStyle}>{formatTime(a.clock_in)}</td>
                        <td style={tdStyle}>{formatTime(a.clock_out)}</td>
                        <td style={tdStyle}>{formatMinutes(a.work_minutes)}</td>
                        <td style={tdStyle}>
                          {isDone ? (
                            <span style={{ display: 'inline-block', padding: '2px 10px', borderRadius: '12px', fontSize: '12px', backgroundColor: '#e8f5e9', color: '#2e7d32', fontWeight: 600 }}>退勤済</span>
                          ) : isWorking ? (
                            <span style={{ display: 'inline-block', padding: '2px 10px', borderRadius: '12px', fontSize: '12px', backgroundColor: '#fff9c4', color: '#f57f17', fontWeight: 600 }}>勤務中</span>
                          ) : (
                            <span style={{ display: 'inline-block', padding: '2px 10px', borderRadius: '12px', fontSize: '12px', backgroundColor: '#f5f5f5', color: '#9e9e9e', fontWeight: 600 }}>未出勤</span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            )}
          </>
        )}

        {tab === 'leave' && (
          <>
            <h3 style={{ margin: '0 0 20px', fontSize: '16px', color: '#1a237e' }}>休暇申請一覧</h3>
            {loadingL ? (
              <div style={{ textAlign: 'center', padding: '32px', color: '#666' }}>読み込み中...</div>
            ) : leaveRequests.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '32px', color: '#999' }}>申請がありません</div>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    {['申請者', '開始日', '終了日', '理由', 'ステータス', '操作'].map(h => (
                      <th key={h} style={thStyle}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {leaveRequests.map(r => {
                    const s = STATUS_LABEL[r.status] || STATUS_LABEL.pending
                    return (
                      <tr key={r.id}>
                        <td style={{ ...tdStyle, fontWeight: 600 }}>{r.user_id}</td>
                        <td style={tdStyle}>{r.start_date}</td>
                        <td style={tdStyle}>{r.end_date}</td>
                        <td style={{ ...tdStyle, maxWidth: '200px' }}>{r.reason}</td>
                        <td style={tdStyle}>
                          <span style={{ display: 'inline-block', padding: '2px 10px', borderRadius: '12px', fontSize: '12px', backgroundColor: s.bg, color: s.color, fontWeight: 600 }}>
                            {s.label}
                          </span>
                        </td>
                        <td style={tdStyle}>
                          {r.status === 'pending' && (
                            <div style={{ display: 'flex', gap: '8px' }}>
                              <button
                                onClick={() => handleLeaveAction(r.id, 'approved')}
                                style={{ padding: '4px 12px', backgroundColor: '#2e7d32', color: '#fff', border: 'none', borderRadius: '6px', fontSize: '13px', cursor: 'pointer' }}
                              >承認</button>
                              <button
                                onClick={() => handleLeaveAction(r.id, 'rejected')}
                                style={{ padding: '4px 12px', backgroundColor: '#c62828', color: '#fff', border: 'none', borderRadius: '6px', fontSize: '13px', cursor: 'pointer' }}
                              >却下</button>
                            </div>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            )}
          </>
        )}
      </div>
    </div>
  )
}
