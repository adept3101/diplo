import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';

function Login() {
  const [formData, setFormData] = useState({ login: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/auth/login', formData);
      if (response.data['access token']) {
        localStorage.setItem('token', response.data['access token']);
      }
      navigate('/profile/me');
    } catch (err) {
      setError(err.response?.status === 401 ? 'Неверный логин или пароль' : 'Ошибка доступа к API');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#fafafa",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontFamily: "'DM Sans', system-ui, sans-serif",
      color: "#111",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=DM+Sans:wght@400;500;600&display=swap');
        @keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
        input:focus { outline: none; border-color: #111 !important; box-shadow: 0 0 0 1px #111; }
        .auth-card { animation: fade-in 0.4s ease; }
      `}</style>

      <div className="auth-card" style={{
        width: "100%",
        maxWidth: "400px",
        padding: "40px",
        background: "#fff",
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        boxShadow: "0 4px 20px rgba(0,0,0,0.03)"
      }}>
        
        {/* Logo / Title */}
        <div style={{ marginBottom: "32px", textAlign: "center" }}>
          <div style={{ 
            fontFamily: "'IBM Plex Mono', monospace", 
            fontWeight: 600, 
            fontSize: "18px", 
            letterSpacing: "-0.02em",
            marginBottom: "8px"
          }}>
            fx.auth
          </div>
          <div style={{ color: "#9ca3af", fontSize: "12px" }}>
            Введите учетные данные для доступа
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "20px" }}>
            <label style={{
              display: "block",
              fontSize: "10px",
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              color: "#9ca3af",
              fontFamily: "'IBM Plex Mono', monospace",
              marginBottom: "8px"
            }}>Логин</label>
            <input
              type="text"
              name="login"
              value={formData.login}
              onChange={handleChange}
              required
              style={{
                width: "100%",
                padding: "12px",
                border: "1px solid #e5e7eb",
                borderRadius: "6px",
                fontSize: "14px",
                fontFamily: "'IBM Plex Mono', monospace",
                transition: "all 0.2s"
              }}
            />
          </div>

          <div style={{ marginBottom: "24px" }}>
            <label style={{
              display: "block",
              fontSize: "10px",
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              color: "#9ca3af",
              fontFamily: "'IBM Plex Mono', monospace",
              marginBottom: "8px"
            }}>Пароль</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              style={{
                width: "100%",
                padding: "12px",
                border: "1px solid #e5e7eb",
                borderRadius: "6px",
                fontSize: "14px",
                fontFamily: "'IBM Plex Mono', monospace",
                transition: "all 0.2s"
              }}
            />
          </div>

          {error && (
            <div style={{
              marginBottom: "20px",
              padding: "10px",
              background: "#fef2f2",
              border: "1px solid #fecaca",
              borderRadius: "6px",
              color: "#dc2626",
              fontSize: "12px",
              fontFamily: "'IBM Plex Mono', monospace",
            }}>
              ⚠ {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px",
              background: loading ? "#f3f4f6" : "#111",
              color: loading ? "#9ca3af" : "#fff",
              border: "none",
              borderRadius: "6px",
              fontWeight: 600,
              fontSize: "13px",
              fontFamily: "'IBM Plex Mono', monospace",
              cursor: loading ? "not-allowed" : "pointer",
              transition: "all 0.15s",
              letterSpacing: "0.04em"
            }}
          >
            {loading ? "CHECKING..." : "ENTER_SYSTEM →"}
          </button>
        </form>

        <div style={{ 
          marginTop: "32px", 
          textAlign: "center",
          fontSize: "12px",
          color: "#9ca3af"
        }}>
          Нет аккаунта?{' '}
          <Link to="/auth/register" style={{ 
            color: "#111", 
            textDecoration: "none", 
            fontWeight: 600,
            borderBottom: "1px solid #e5e7eb"
          }}>
            Создать профиль
          </Link>
        </div>

      </div>
    </div>
  );
}

export default Login;
