import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Login from './components/login';
import Register from './components/register';
import CurrForecast from './components/CurrForecast';
import Profile from './components/profile';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Выносим логику в отдельный компонент, чтобы useLocation работал внутри Router
function AppLayout() {
  const location = useLocation();
  
  // На страницах авторизации navbar и footer не нужны
  const isAuthPage = ['/auth/login', '/auth/register'].includes(location.pathname);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {!isAuthPage && <Navbar />}

      <main style={{ flex: 1 }}>
        <Routes>
          <Route path="/auth/login" element={<Login />} />
          <Route path="/auth/register" element={<Register />} />
          <Route path="/course/currency" element={<CurrForecast />} />
          <Route path="/profile/me" element={<Profile />} />
        </Routes>
      </main>

      {!isAuthPage && <Footer />}
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppLayout />
    </Router>
  );
}

export default App;
