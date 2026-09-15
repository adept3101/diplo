import React, { useEffect, useState } from 'react';
// import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const Profile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

// const navigate = useNavigate();

// const handleLogout = async () => {
//   try {
//     await api.post('/auth/logout');
//
//     localStorage.removeItem('token'); 
//
//     navigate('/auth/login');
//   } catch (err) {
//     console.error("Ошибка при выходе:", err);
//     navigate('/auth/login');
//   }
// };

  useEffect(() => {
    setLoading(true);
    api.get('/profile/me')
      .then(res => {
        setUser(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Не авторизован", err);
        setError("Пользователь не авторизован");
        setLoading(false);
      });
  }, []);

  return (
    <div style={{
      minHeight: "100vh",
      background: "#fafafa",
      color: "#111",
      fontFamily: "'DM Sans', system-ui, sans-serif",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=DM+Sans:wght@400;500;600&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @keyframes fade-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
      `}</style>

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "24px 24px 48px" }}>
        
        
        {error && (
          <div style={{
            marginTop: 16, padding: "10px 14px",
            background: "#fef2f2", border: "1px solid #fecaca",
            borderRadius: 6, color: "#dc2626",
            fontFamily: "'IBM Plex Mono', monospace", fontSize: 12,
            animation: "fade-in 0.3s ease",
          }}>
            ⚠ {error}
          </div>
        )}

        <div style={{ display: "flex", gap: 32, marginTop: 28, alignItems: "flex-start" }}>
          
          {/* ── Center Content ── */}
          <div style={{ flex: 1, minWidth: 0, animation: "fade-in 0.4s ease" }}>
            {loading ? (
              <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 14, color: "#9ca3af" }}>
                Загрузка данных профиля…
              </div>
            ) : user ? (
              <>
                <div style={{
                  paddingBottom: 18, borderBottom: "1px solid #e5e7eb",
                  marginBottom: 24
                }}>
                  <div style={{
                    fontFamily: "'IBM Plex Mono', monospace", fontSize: 32,
                    fontWeight: 600, letterSpacing: "-0.04em", lineHeight: 1,
                  }}>
                    {user.login}
                    <span style={{ fontSize: 14, color: "#16a34a", marginLeft: 12, fontWeight: 400 }}>
                      online
                    </span>
                  </div>
                  <div style={{
                    fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, marginTop: 8,
                    color: "#6b7280"
                  }}>
                    ID пользователя: {user.id || 'N/A'}
                  </div>
                </div>

                {/* Инфо-карточки */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 16 }}>
                  {[
                    ["Роль", user.role || "User"],
                    ["Дата регистрации", user.date || "—"],
                    ["Статус", "Верифицирован"]
                  ].map(([k, v]) => (
                    <div key={k} style={{
                      padding: "16px", background: "#fff", border: "1px solid #e5e7eb",
                      borderRadius: 8, boxShadow: "0 1px 2px rgba(0,0,0,0.02)"
                    }}>
                      <div style={{
                        fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase",
                        color: "#9ca3af", fontFamily: "'IBM Plex Mono', monospace", marginBottom: 8,
                      }}>{k}</div>
                      <div style={{
                        fontFamily: "'IBM Plex Mono', monospace", fontSize: 14, fontWeight: 600, color: "#111"
                      }}>{v}</div>
                    </div>
                  ))}
                </div>
              </>
            ) : null}
          </div>


            
            {/* <div style={{  */}
              {/* marginTop: 32, padding: "12px", borderRadius: 8,  */}
              {/* background: "linear-gradient(135deg, #111, #333)", color: "#fff"  */}
            {/* }}> */}
               {/* <div style={{ fontSize: 10, fontFamily: "'IBM Plex Mono', monospace", opacity: 0.7, marginBottom: 4 }}>Тариф</div> */}
               {/* <div style={{ fontSize: 13, fontWeight: 600, fontFamily: "'IBM Plex Mono', monospace" }}>PRO Analyst</div> */}
            {/* </div> */}
          </div>

        </div>
      </div>
    // </div>
  );
};

export default Profile;
