import React from 'react';
import { BrowserRouter as Router, Routes, Route} from 'react-router-dom'; //Navigate deleted
import Login from './components/login';
import Register from './components/register';
import CurrForecast from './components/CurrForecast'
import Profile from './components/profile'
// Компонент для защищенных маршрутов
// function PrivateRoute({ children }) {
//   const token = localStorage.getItem('token');
//   return token ? children : <Navigate to="/login" />;
// }

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/auth/login" element={<Login />} />
          <Route path="/auth/register" element={<Register />} />
          <Route path="/course/currency" element={<CurrForecast />} />
          {/* <Route path="/course/predict" element={<CurrForecast />} /> */}
          <Route path="/profile/me" element={<Profile />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
