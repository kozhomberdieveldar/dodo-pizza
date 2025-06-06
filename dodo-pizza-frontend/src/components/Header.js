// src/components/Header.js
import React from 'react';
import { Link } from 'react-router-dom';

export default function Header() {
  return (
    <header style={{
      backgroundColor: '#ff5a00',
      padding: '10px 20px',
      display: 'flex',
      alignItems: 'center',
      color: 'white',
      fontWeight: '700',
      fontSize: '20px'
    }}>
      <img
        src="/images/dodo-logo.png"
        alt="Dodo Pizza"
        style={{ width: '50px', height: '50px', marginRight: '20px' }}
      />
      <nav>
        <Link to="/" style={{ color: 'white', marginRight: '20px', textDecoration: 'none' }}>Главная</Link>
        <Link to="/search" style={{ color: 'white', marginRight: '20px', textDecoration: 'none' }}>Поиск</Link>
        <Link to="/cart" style={{ color: 'white', textDecoration: 'none' }}>Корзина</Link>
      </nav>
    </header>
  );
}
