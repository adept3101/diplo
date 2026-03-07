import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';

function Register() {
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
      const response = await api.post('/auth/register', formData);
      console.log('Регистрация успешна:', response.data);
      
      // После успешной регистрации, автоматически логиним пользователя
      const loginResponse = await api.post('/auth/login', formData);
      
      // Сохраняем токен в localStorage (если используете cookies, это может быть не нужно)
      if (loginResponse.data['access token']) {
        localStorage.setItem('token', loginResponse.data['access token']);
      }
      
      navigate('/dashboard'); // перенаправляем на защищенную страницу
    } catch (err) {
      if (err.response?.status === 400) {
        setError('Пользователь с таким логином уже существует');
      } else {
        setError('Ошибка регистрации.');
      }
      console.error('Ошибка регистрации:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2>Регистрация</h2>
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
            minLength="3"
            maxLength="50"
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
            minLength="6"
          />
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <button type="submit" disabled={loading}>
          {loading ? 'Регистрация...' : 'Зарегистрироваться'}
        </button>
      </form>
      
      <p>
        Уже есть аккаунт? <Link to="/auth/login">Войти</Link>
      </p>
    </div>
  );
}

export default Register;
