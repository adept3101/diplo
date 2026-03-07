import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { RefreshCcw, Calendar, Search, AlertCircle } from 'lucide-react';

const CurrencyViewer = () => {
  const [rates, setRates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]); // YYYY-MM-DD
  const [search, setSearch] = useState('');

  // Форматируем дату для API CBR (dd/mm/yyyy)
  const formatDataForApi = (isoDate) => {
    const [year, month, day] = isoDate.split('-');
    return `${day}/${month}/${year}`;
  };

  const fetchRates = useCallback( async () => {
    setLoading(true);
    setError(null);
    try {
      // Заменяем URL на адрес твоего FastAPI сервера
      const formattedDate = formatDataForApi(date);
      const response = await axios.get(`http://localhost:8000/course/`, {
        params: { date_req: formattedDate }
      });
      setRates(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Ошибка при загрузке данных");
    } finally {
      setLoading(false);
    }
  }, [date]);

  useEffect(() => {
    fetchRates();
  }, [fetchRates]);

  const filteredRates = rates.filter(r => 
    r.code.toLowerCase().includes(search.toLowerCase()) || 
    r.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-50 min-h-screen font-sans">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-800">Курсы валют ЦБ РФ</h1>
        <p className="text-gray-500">Данные в реальном времени из XML-сервиса</p>
      </header>

      {/* Панель управления */}
      <div className="bg-white p-4 rounded-xl shadow-sm mb-6 flex flex-wrap gap-4 items-center justify-between">
        <div className="flex items-center gap-2 bg-gray-100 p-2 rounded-lg">
          <Calendar size={20} className="text-blue-500" />
          <input 
            type="date" 
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="bg-transparent border-none focus:ring-0 text-gray-700 outline-none"
          />
        </div>

        <div className="flex-1 min-w-[200px] relative">
          <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
          <input 
            type="text"
            placeholder="Поиск валюты (USD, EUR...)"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400"
          />
        </div>

        <button 
          onClick={fetchRates}
          disabled={loading}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
        >
          <RefreshCcw size={18} className={loading ? 'animate-spin' : ''} />
          Обновить
        </button>
      </div>

      {/* Ошибки */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 flex items-center gap-3 text-red-700">
          <AlertCircle />
          <p>{error}</p>
        </div>
      )}

      {/* Сетка с карточками */}
      {loading ? (
        <div className="text-center py-20 text-gray-400">Загрузка актуальных курсов...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRates.map((item) => (
            <div key={item.code} className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition">
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs font-bold bg-blue-100 text-blue-700 px-2 py-1 rounded">
                  {item.nominal} {item.code}
                </span>
                <span className="text-xl font-mono font-semibold text-green-600">
                  {item.value} ₽
                </span>
              </div>
              <h3 className="text-gray-700 font-medium leading-tight">{item.name}</h3>
            </div>
          ))}
        </div>
      )}

      {filteredRates.length === 0 && !loading && !error && (
        <div className="text-center py-10 text-gray-400">Ничего не найдено</div>
      )}
    </div>
  );
};

export default CurrencyViewer;
