import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Header from './components/Header';
import BottomNav from './components/BottomNav';
import TopNav from './components/TopNav';  // <-- импортируем TopNav

import Home from './pages/Home';
import Search from './pages/Search';
import CartPage from './pages/CartPage';

function App() {
  return (
    <Router>
      <Header />
      <TopNav />       {/* <-- вставляем TopNav сюда */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<Search />} />
        <Route path="/cart" element={<CartPage />} />
      </Routes>
      <BottomNav />
    </Router>
  );
}

export default App;
