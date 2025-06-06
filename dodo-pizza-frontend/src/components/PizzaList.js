// src/components/PizzaList.js
import React, { useEffect, useState } from 'react';
import PizzaCard from './PizzaCard';

export default function PizzaList() {
  const [pizzas, setPizzas] = useState([]);

  useEffect(() => {
    // Запрос к бэкенду, замени URL на твой API эндпоинт
    fetch('http://localhost:8000/api/pizzas/')
      .then(res => res.json())
      .then(data => setPizzas(data))
      .catch(console.error);
  }, []);

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', padding: '20px' }}>
      {pizzas.map(pizza => (
        <PizzaCard key={pizza.id} pizza={pizza} />
      ))}
    </div>
  );
}
