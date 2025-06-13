import { useState } from 'react'
import './App.css'
import Cart from './Cart'
import Register from './Register'

function App() {
  const [showRegister, setShowRegister] = useState(false)

  return (
    <div className="app">
      <header>
        <h1>Dodo Pizza</h1>
        <button 
          className="auth-button"
          onClick={() => setShowRegister(!showRegister)}
        >
          {showRegister ? 'Закрыть регистрацию' : 'Регистрация'}
        </button>
      </header>

      {showRegister ? (
        <Register />
      ) : (
        <main>
          <Cart />
        </main>
      )}
    </div>
  )
}

export default App
