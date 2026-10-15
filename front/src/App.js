import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import CurrForecast from './components/CurrForecast';
import Profile from './components/Profile';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

function AppLayout() {
  const location = useLocation();
  
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
