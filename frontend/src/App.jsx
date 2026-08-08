import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

import Sidebar from './components/Sidebar';
import ProtectedRoute from './components/ProtectedRoute';

import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Meters from './pages/Meters';
import MeterDetail from './pages/MeterDetail';
import Alerts from './pages/Alerts';
import Reports from './pages/Reports';

function AppLayout({ children }) {
  return (
    <div className="min-h-screen bg-surface-950">
      <Sidebar />
      <main className="ml-[260px] p-6 lg:p-8 max-w-[1400px]">
        {children}
      </main>
    </div>
  );
}

export default function App() {
  const { user } = useAuth();

  return (
    <Routes>
      {/* ─── Public routes ──────────────────────────────── */}
      <Route
        path="/login"
        element={user ? <Navigate to="/" replace /> : <Login />}
      />
      <Route
        path="/register"
        element={user ? <Navigate to="/" replace /> : <Register />}
      />

      {/* ─── Protected routes ───────────────────────────── */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Dashboard />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/meters"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Meters />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/meters/:id"
        element={
          <ProtectedRoute>
            <AppLayout>
              <MeterDetail />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/alerts"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Alerts />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/reports"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Reports />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      {/* ─── Catch-all ──────────────────────────────────── */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
