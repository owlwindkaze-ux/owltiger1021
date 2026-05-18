import React, { useState, useEffect } from 'react'
import { format, startOfMonth } from 'date-fns'
import { attendanceApi, MonthlySummary } from '../api'
import AttendanceClock from './AttendanceClock'

function formatTime(isoString: string | null): string {
  if (!isoString) return '--:--'
  return new Date(isoString).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
}

function formatMinutes(minutes: number): string {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (h === 0) return `${m}分`
  return `${h}時間${m}分`
}

export default function Dashboard() {
  const [currentMonth, setCurrentMonth] = useState(() =>
    format(startOfMonth(new Date()), 'yyyy-MM')
  )
  const [summary, setSummary] = useState<MonthlySummary | null>(null)
  const [summaryLoading, setSummaryLoading] = useState(false)

  useEffect(() => {
    setSummaryLoading(true)
    attendanceApi
      .summary(currentMonth)
      .then((res) => setSummary(res.data))
      .catch(() => setSummary(null))
      .finally(() => setSummaryLoading(false))
  }, [currentMonth])

  const pageStyle: React.CSSProperties = {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '32px 24px',
  }

  const sectionTitleStyle: React.CSSProperties = {
    fontSize: '18px',
    fontWeight: 700,
    color: '#1a237e',
    marginBottom: '16px',
  }

  const cardStyle: React.CSSProperties = {
    backgroundColor: '#fff',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
    marginBottom: '24px',
  }

  const statBadgeStyle: React.CSSProperties = {
    display: 'inline-flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '16px 28px',
    backgroundColor: '#e8eaf6',
    borderRadius: '10px',
    marginRight: '16px',
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
  }

  const monthNavStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '20px',
  }

  const navBtnStyle: React.CSSProperties = {
    padding: '6px 14px',
    border: '1px solid #c5cae9',
    borderRadius: '6px',
    backgroundColor: '#fff',
    color: '#3949ab',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 600,
  }

  const changeMonth = (delta: number) => {
    const [year, mon] = currentMonth.split('-').map(Number)
    const d = new Date(year, mon - 1 + delta, 1)
    setCurrentMonth(format(d, 'yyyy-MM'))
  }

  const [year, mon] = currentMonth.split('-')

  return (
    <div style={pageStyle}>
      <h2 style={{ fontSize: '22px', fontWeight: 700, color: '#333', marginBottom: '24px' }}>
        ダッシュボード
      </h2>

      <AttendanceClock />

      <div style={cardStyle}>
        <div style={monthNavStyle}>
          <h3 style={{ ...sectionTitleStyle, marginBottom: 0 }}>月次勤務サマリ</h3>
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button style={navBtnStyle} onClick={() => changeMonth(-1)}>◀</button>
            <span style={{ fontSize: '16px', fontWeight: 600, color: '#1a237e', minWidth: '90px', textAlign: 'center' }}>
              {year}年{mon}月
            </span>
            <button style={navBtnStyle} onClick={() => changeMonth(1)}>▶</button>
          </div>
        </div>

        {summary && (
          <div style={{ display: 'flex', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
            <div style={statBadgeStyle}>
              <span style={{ fontSize: '24px', fontWeight: 700, color: '#1a237e' }}>
                {summary.work_days}
              </span>
              <span style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>出勤日数</span>
            </div>
            <div style={statBadgeStyle}>
              <span style={{ fontSize: '24px', fontWeight: 700, color: '#1a237e' }}>
                {formatMinutes(summary.total_work_minutes)}
              </span>
              <span style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>総勤務時間</span>
            </div>
            <div style={statBadgeStyle}>
              <span style={{ fontSize: '24px', fontWeight: 700, color: '#1a237e' }}>
                {summary.work_days > 0
                  ? formatMinutes(Math.round(summary.total_work_minutes / summary.work_days))
                  : '--'}
              </span>
              <span style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>平均勤務時間/日</span>
            </div>
          </div>
        )}

        {summaryLoading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>読み込み中...</div>
        ) : summary && summary.records.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={tableStyle}>
              <thead>
                <tr>
                  <th style={thStyle}>日付</th>
                  <th style={thStyle}>出勤</th>
                  <th style={thStyle}>退勤</th>
                  <th style={thStyle}>勤務時間</th>
                  <th style={thStyle}>ステータス</th>
                </tr>
              </thead>
              <tbody>
                {summary.records.map((r) => {
                  const dateObj = new Date(r.date + 'T00:00:00')
                  const isComplete = !!r.clock_in && !!r.clock_out
                  const isInProgress = !!r.clock_in && !r.clock_out
                  return (
                    <tr key={r.date} style={{ backgroundColor: isInProgress ? '#fffde7' : '#fff' }}>
                      <td style={tdStyle}>
                        {dateObj.toLocaleDateString('ja-JP', { month: 'numeric', day: 'numeric', weekday: 'short' })}
                      </td>
                      <td style={tdStyle}>{formatTime(r.clock_in)}</td>
                      <td style={tdStyle}>{formatTime(r.clock_out)}</td>
                      <td style={tdStyle}>
                        {r.work_minutes > 0 ? formatMinutes(r.work_minutes) : '--'}
                      </td>
                      <td style={tdStyle}>
                        {isComplete ? (
                          <span style={{
                            display: 'inline-block',
                            padding: '2px 10px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            backgroundColor: '#e8f5e9',
                            color: '#2e7d32',
                            fontWeight: 600,
                          }}>完了</span>
                        ) : isInProgress ? (
                          <span style={{
                            display: 'inline-block',
                            padding: '2px 10px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            backgroundColor: '#fff9c4',
                            color: '#f57f17',
                            fontWeight: 600,
                          }}>勤務中</span>
                        ) : (
                          <span style={{
                            display: 'inline-block',
                            padding: '2px 10px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            backgroundColor: '#f5f5f5',
                            color: '#9e9e9e',
                            fontWeight: 600,
                          }}>未出勤</span>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: '#bbb', fontSize: '14px' }}>
            この月の勤怠記録はありません
          </div>
        )}
      </div>
    </div>
  )
}
