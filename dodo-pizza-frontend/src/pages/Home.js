// src/pages/Home.js
import React from 'react';
import PizzaList from '../components/PizzaList';

export default function Home() {
  return (
    <div style={{ paddingBottom: '60px' }}> {/* чтобы не налезала нижняя панель */}
      <PizzaList />
    </div>
  );
}
