import React, { useState, useEffect } from 'react'
import { leaveApi, LeaveRequest as LeaveRequestType } from '../api'

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, React.CSSProperties> = {
    pending: {
      backgroundColor: '#fff9c4',
      color: '#f57f17',
    },
    approved: {
      backgroundColor: '#e8f5e9',
      color: '#2e7d32',
    },
    rejected: {
      backgroundColor: '#ffebee',
      color: '#c62828',
    },
  }
  const labels: Record<string, string> = {
    pending: '審査中',
    approved: '承認済み',
    rejected: '却下',
  }
  return (
    <span style={{
      display: 'inline-block',
      padding: '3px 12px',
      borderRadius: '12px',
      fontSize: '12px',
      fontWeight: 600,
      ...(styles[status] ?? { backgroundColor: '#f5f5f5', color: '#666' }),
    }}>
      {labels[status] ?? status}
    </span>
  )
}

export default function LeaveRequest() {
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [reason, setReason] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [submitSuccess, setSubmitSuccess] = useState(false)
  const [requests, setRequests] = useState<LeaveRequestType[]>([])
  const [loadingList, setLoadingList] = useState(true)

  const loadRequests = () => {
    setLoadingList(true)
    leaveApi
      .myRequests()
      .then((res) => setRequests(res.data))
      .catch(() => setRequests([]))
      .finally(() => setLoadingList(false))
  }

  useEffect(() => {
    loadRequests()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitError('')
    setSubmitSuccess(false)
    if (endDate < startDate) {
      setSubmitError('終了日は開始日以降にしてください')
      return
    }
    setSubmitting(true)
    try {
      await leaveApi.request({ start_date: startDate, end_date: endDate, reason })
      setSubmitSuccess(true)
      setStartDate('')
      setEndDate('')
      setReason('')
      loadRequests()
      setTimeout(() => setSubmitSuccess(false), 4000)
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      setSubmitError(axiosErr.response?.data?.detail ?? '申請に失敗しました')
    } finally {
      setSubmitting(false)
    }
  }

  const pageStyle: React.CSSProperties = {
    maxWidth: '820px',
    margin: '0 auto',
    padding: '32px 24px',
  }

  const cardStyle: React.CSSProperties = {
    backgroundColor: '#fff',
    borderRadius: '12px',
    padding: '28px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
    marginBottom: '24px',
  }

  const labelStyle: React.CSSProperties = {
    display: 'block',
    marginBottom: '6px',
    fontSize: '13px',
    fontWeight: 600,
    color: '#444',
  }

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '9px 12px',
    border: '1.5px solid #e0e0e0',
    borderRadius: '7px',
    fontSize: '14px',
    outline: 'none',
    boxSizing: 'border-box',
    marginBottom: '16px',
  }

  const textareaStyle: React.CSSProperties = {
    ...inputStyle,
    resize: 'vertical',
    minHeight: '90px',
    fontFamily: 'inherit',
  }

  const submitBtnStyle: React.CSSProperties = {
    padding: '10px 28px',
    backgroundColor: submitting ? '#9fa8da' : '#1a237e',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: 600,
    cursor: submitting ? 'not-allowed' : 'pointer',
  }

  const tableStyle: React.CSSProperties = {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '14px',
  }

  const thStyle: React.CSSProperties = {
    padding: '10px 12px',
    textAlign: 'left',
    backgroundColor: '#f5f5f5',
    color: '#555',
    fontWeight: 600,
    fontSize: '13px',
    borderBottom: '2px solid #e0e0e0',
  }

  const tdStyle: React.CSSProperties = {
    padding: '10px 12px',
    borderBottom: '1px solid #f0f0f0',
    color: '#333',
    verticalAlign: 'middle',
  }

  return (
    <div style={pageStyle}>
      <h2 style={{ fontSize: '22px', fontWeight: 700, color: '#333', marginBottom: '24px' }}>
        休暇申請
      </h2>

      {/* Form card */}
      <div style={cardStyle}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#1a237e', marginBottom: '20px' }}>
          新規申請
        </h3>

        {submitSuccess && (
          <div style={{
            backgroundColor: '#e8f5e9',
            color: '#2e7d32',
            padding: '10px 14px',
            borderRadius: '8px',
            fontSize: '13px',
            marginBottom: '16px',
            borderLeft: '4px solid #43a047',
          }}>
            休暇申請を送信しました。管理者の承認をお待ちください。
          </div>
        )}

        {submitError && (
          <div style={{
            backgroundColor: '#ffebee',
            color: '#c62828',
            padding: '10px 14px',
            borderRadius: '8px',
            fontSize: '13px',
            marginBottom: '16px',
            borderLeft: '4px solid #e53935',
          }}>
            {submitError}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'flex', gap: '16px' }}>
            <div style={{ flex: 1 }}>
              <label style={labelStyle} htmlFor="startDate">開始日</label>
              <input
                id="startDate"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                style={inputStyle}
                required
              />
            </div>
            <div style={{ flex: 1 }}>
              <label style={labelStyle} htmlFor="endDate">終了日</label>
              <input
                id="endDate"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                style={inputStyle}
                required
              />
            </div>
          </div>

          <label style={labelStyle} htmlFor="reason">申請理由</label>
          <textarea
            id="reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            style={textareaStyle}
            placeholder="休暇の理由を入力してください"
            required
          />

          <button type="submit" style={submitBtnStyle} disabled={submitting}>
            {submitting ? '送信中...' : '申請する'}
          </button>
        </form>
      </div>

      {/* List card */}
      <div style={cardStyle}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#1a237e', marginBottom: '20px' }}>
          申請履歴
        </h3>

        {loadingList ? (
          <div style={{ padding: '32px', textAlign: 'center', color: '#999' }}>読み込み中...</div>
        ) : requests.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: '#bbb', fontSize: '14px' }}>
            申請履歴はありません
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={tableStyle}>
              <thead>
                <tr>
                  <th style={thStyle}>開始日</th>
                  <th style={thStyle}>終了日</th>
                  <th style={thStyle}>理由</th>
                  <th style={thStyle}>申請日</th>
                  <th style={thStyle}>ステータス</th>
                </tr>
              </thead>
              <tbody>
                {requests.map((req) => (
                  <tr key={req.id}>
                    <td style={tdStyle}>{req.start_date}</td>
                    <td style={tdStyle}>{req.end_date}</td>
                    <td style={{ ...tdStyle, maxWidth: '200px' }}>
                      <span style={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {req.reason}
                      </span>
                    </td>
                    <td style={tdStyle}>
                      {new Date(req.created_at).toLocaleDateString('ja-JP')}
                    </td>
                    <td style={tdStyle}>
                      <StatusBadge status={req.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
