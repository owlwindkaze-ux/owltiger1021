import React from 'react'
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import LeaveRequest from './components/LeaveRequest'
import AdminDashboard from './components/AdminDashboard'
import { User } from './api'

function getStoredUser(): User | null {
  try {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function NavBar({ user, onLogout }: { user: User; onLogout: () => void }) {
  const location = useLocation()

  const navStyle: React.CSSProperties = {
    backgroundColor: '#1a237e',
    color: '#fff',
    padding: '0 24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: '60px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
  }

  const brandStyle: React.CSSProperties = {
    fontSize: '18px',
    fontWeight: 700,
    color: '#fff',
    textDecoration: 'none',
  }

  const navLinksStyle: React.CSSProperties = {
    display: 'flex',
    gap: '8px',
    alignItems: 'center',
  }

  const linkStyle = (active: boolean): React.CSSProperties => ({
    color: active ? '#fff' : 'rgba(255,255,255,0.75)',
    textDecoration: 'none',
    padding: '6px 14px',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: active ? 600 : 400,
    backgroundColor: active ? 'rgba(255,255,255,0.2)' : 'transparent',
    transition: 'all 0.2s',
  })

  const logoutBtnStyle: React.CSSProperties = {
    backgroundColor: 'transparent',
    border: '1px solid rgba(255,255,255,0.5)',
    color: '#fff',
    padding: '6px 14px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    marginLeft: '8px',
  }

  const userInfoStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  }

  return (
    <nav style={navStyle}>
      <Link to="/dashboard" style={brandStyle}>🏢 勤怠管理システム</Link>
      <div style={navLinksStyle}>
        <Link to="/dashboard" style={linkStyle(location.pathname === '/dashboard')}>ダッシュボード</Link>
        <Link to="/leave" style={linkStyle(location.pathname === '/leave')}>休暇申請</Link>
        {user.role === 'admin' && (
          <Link to="/admin" style={linkStyle(location.pathname === '/admin')}>管理者画面</Link>
        )}
        <div style={userInfoStyle}>
          <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.85)' }}>
            {user.full_name}
            <span style={{
              marginLeft: '6px',
              fontSize: '11px',
              backgroundColor: user.role === 'admin' ? '#ff6f00' : '#1565c0',
              padding: '2px 6px',
              borderRadius: '10px',
              color: '#fff',
            }}>
              {user.role === 'admin' ? '管理者' : '社員'}
            </span>
          </span>
          <button style={logoutBtnStyle} onClick={onLogout}>ログアウト</button>
        </div>
      </div>
    </nav>
  )
}

function ProtectedRoute({ children, adminOnly = false }: { children: React.ReactNode; adminOnly?: boolean }) {
  const user = getStoredUser()
  const token = localStorage.getItem('token')

  if (!token || !user) {
    return <Navigate to="/login" replace />
  }

  if (adminOnly && user.role !== 'admin') {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

function AppLayout({ children }: { children: React.ReactNode }) {
  const user = getStoredUser()

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  if (!user) return null

  return (
    <>
      <NavBar user={user} onLogout={handleLogout} />
      <main style={{ minHeight: 'calc(100vh - 60px)', backgroundColor: '#f0f2f5' }}>
        {children}
      </main>
    </>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <AppLayout><Dashboard /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/leave"
          element={
            <ProtectedRoute>
              <AppLayout><LeaveRequest /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute adminOnly>
              <AppLayout><AdminDashboard /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
