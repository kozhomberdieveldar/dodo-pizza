import { useState } from 'react';
import './Register.css';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    phone: '',
    address: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const response = await fetch('http://localhost:8000/api/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setSuccess('Регистрация успешна! Теперь вы можете войти.');
        // Очищаем форму
        setFormData({
          username: '',
          email: '',
          password: '',
          phone: '',
          address: ''
        });
      } else {
        const data = await response.json();
        // Если есть несколько ошибок, выводим их все
        if (typeof data === 'object' && data !== null) {
          let errorMsg = '';
          for (const key in data) {
            if (Array.isArray(data[key])) {
              errorMsg += `${key}: ${data[key].join(', ')}\n`;
            } else {
              errorMsg += `${key}: ${data[key]}\n`;
            }
          }
          setError(errorMsg.trim());
          console.error('Ошибка регистрации:', data);
        } else {
          setError(data.detail || 'Ошибка при регистрации');
          console.error('Ошибка регистрации:', data);
        }
      }
    } catch (err) {
      setError('Ошибка сети или сервера');
    }
  };

  return (
    <div className="register-container">
      <h2>Регистрация</h2>
      <form onSubmit={handleSubmit} className="register-form">
        <div className="form-group">
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Имя пользователя"
            required
          />
        </div>
        <div className="form-group">
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Email"
            required
          />
        </div>
        <div className="form-group">
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Пароль"
            required
          />
        </div>
        <div className="form-group">
          <input
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            placeholder="Телефон"
            required
          />
        </div>
        <div className="form-group">
          <input
            type="text"
            name="address"
            value={formData.address}
            onChange={handleChange}
            placeholder="Адрес"
            required
          />
        </div>
        <button type="submit">Зарегистрироваться</button>
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
      </form>
    </div>
  );
};

export default Register; 