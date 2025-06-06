// src/components/BottomNav.js
import React from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function BottomNav() {
  const location = useLocation();

  const activeStyle = {
    color: '#ff5a00',
    fontWeight: 'bold'
  };

  return (
    <nav style={{
      position: 'fixed',
      bottom: 0,
      width: '100%',
      backgroundColor: 'white',
      borderTop: '1px solid #ddd',
      display: 'flex',
      justifyContent: 'space-around',
      padding: '10px 0'
    }}>
      <Link to="/" style={location.pathname === '/' ? activeStyle : {}}>🏠 Главная</Link>
      <Link to="/search" style={location.pathname === '/search' ? activeStyle : {}}>🔍 Поиск</Link>
      <Link to="/cart" style={location.pathname === '/cart' ? activeStyle : {}}>🛒 Корзина</Link>
    </nav>
  );
}
