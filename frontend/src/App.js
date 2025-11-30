
import React, { useState } from "react";
import { Card, CardContent } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Button } from "./components/ui/button";

export default function App() {
  const API_URL = "http://localhost:8000/course";

  const [date, setDate] = useState("");
  const [allRates, setAllRates] = useState([]);

  const [code, setCode] = useState("USD");
  const [currency, setCurrency] = useState(null);

  const [daysAhead, setDaysAhead] = useState(1);
  const [prediction, setPrediction] = useState(null);

  const getRates = async () => {
    const res = await fetch(`${API_URL}/?date_req=${date}`);
    const data = await res.json();
    setAllRates(data);
  };

  const getCurrency = async () => {
    const res = await fetch(`${API_URL}/currency?name_val=${code}`);
    const data = await res.json();
    setCurrency(data[0] || null);
  };

  const getPrediction = async () => {
    const res = await fetch(`${API_URL}/predict?days_ahead=${daysAhead}`);
    const data = await res.json();
    setPrediction(data.predicted_rate);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto font-sans space-y-8">
      <h1 className="text-4xl font-bold text-center mb-6">Курсы валют — CBR API</h1>

      {/* Блок 1 */}
      <Card className="shadow-lg rounded-2xl">
        <div className="p-4 pb-0"><h2 className="text-xl font-semibold">Получить курсы на дату</h2></div>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <Input
              type="text"
              placeholder="19/11/2025"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
            <Button onClick={getRates}>Получить</Button>
          </div>

          <ul className="space-y-1 list-disc pl-5">
            {allRates.map((r) => (
              <li key={r.code}>
                <b>{r.code}</b> — {r.name} — {r.value}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Блок 2 */}
      <Card className="shadow-lg rounded-2xl">
        <div className="p-4 pb-0"><h2 className="text-xl font-semibold">Получить валюту</h2></div>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <Input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
            <Button onClick={getCurrency}>Получить</Button>
          </div>

          {currency && (
            <p className="text-lg">
              <b>{currency.code}</b> — {currency.name} — {currency.value}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Блок 3 */}
      <Card className="shadow-lg rounded-2xl">
        <div className="p-4 pb-0"><h2 className="text-xl font-semibold">Прогноз курса</h2></div>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <Input
              type="number"
              min="1"
              value={daysAhead}
              onChange={(e) => setDaysAhead(e.target.value)}
            />
            <Button onClick={getPrediction}>Прогнозировать</Button>
          </div>

          {prediction && (
            <p className="text-lg">
              Прогноз через {daysAhead} дней: <b>{prediction}</b>
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
