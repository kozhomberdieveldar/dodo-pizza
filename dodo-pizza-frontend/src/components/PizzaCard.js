// src/components/PizzaCard.js
import React from 'react';

export default function PizzaCard({ pizza }) {
  return (
    <div style={{
      border: '1px solid #ddd',
      borderRadius: '8px',
      width: '200px',
      padding: '10px',
      boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
    }}>
      <img
        src={pizza.image} // ожидается URL картинки пиццы
        alt={pizza.name}
        style={{ width: '100%', borderRadius: '8px' }}
      />
      <h3>{pizza.name}</h3>
      <p>{pizza.description}</p>
      <p><b>{pizza.price} ₽</b></p>
      <button style={{
        backgroundColor: '#ff5a00',
        color: 'white',
        border: 'none',
        padding: '8px 12px',
        borderRadius: '4px',
        cursor: 'pointer',
        width: '100%'
      }}>В корзину</button>
    </div>
  );
}
