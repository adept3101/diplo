import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';

function Login() {
  const [formData, setFormData] = useState({
    login: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/auth/login', formData);
      
      // Сохраняем токен в localStorage (если используете cookies, это может быть не нужно)
      if (response.data['access token']) {
        localStorage.setItem('token', response.data['access token']);
      }
      
      console.log('Вход успешен');
      navigate('/dashboard'); // перенаправляем на защищенную страницу
    } catch (err) {
      if (err.response?.status === 401) {
        setError('Неверный логин или пароль');
      } else {
        setError('Ошибка при входе. Попробуйте снова.');
      }
      console.error('Ошибка входа:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2>Вход в систему</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="login">Логин:</label>
          <input
            type="text"
            id="login"
            name="login"
            value={formData.login}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Пароль:</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <button type="submit" disabled={loading}>
          {loading ? 'Вход...' : 'Войти'}
        </button>
      </form>
      
      <p>
        Нет аккаунта? <Link to="/auth/register">Зарегистрироваться</Link>
      </p>
    </div>
  );
}

export default Login;
