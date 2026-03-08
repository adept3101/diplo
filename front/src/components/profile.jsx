import React, { useEffect, useState } from 'react';
import api from './api'; // наш настроенный клиент

const Profile = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    api.get('/profile/me')
      .then(res => setUser(res.data))
      .catch(err => console.error("Не авторизован", err));
  }, []);

  if (!user) return <div>Загрузка профиля...</div>;

  return (
    <div className="p-6 bg-white rounded-xl shadow-md">
      <h2 className="text-2xl font-bold mb-4">Профиль: {user.login}</h2>
    </div>
  );
};
