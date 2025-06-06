// src/components/TopNav.js
import React from 'react';
import { FaPizzaSlice, FaHamburger, FaIceCream, FaCoffee, FaGlassCheers, FaPepperHot, FaUtensils } from 'react-icons/fa';
import './TopNav.css'; // для стилей

export default function TopNav() {
  const categories = [
    { name: 'Пицца', icon: <FaPizzaSlice /> },
    { name: 'Комбо', icon: <FaHamburger /> },
    { name: 'Закуски', icon: <FaUtensils /> },
    { name: 'Десерты', icon: <FaIceCream /> },
    { name: 'Кофе', icon: <FaCoffee /> },
    { name: 'Напитки', icon: <FaGlassCheers /> },
    { name: 'Соусы', icon: <FaPepperHot /> },
  ];

  return (
    <nav className="top-nav">
      {categories.map((cat) => (
        <button key={cat.name} className="top-nav-button">
          <div className="icon">{cat.icon}</div>
          <div className="label">{cat.name}</div>
        </button>
      ))}
    </nav>
  );
}
