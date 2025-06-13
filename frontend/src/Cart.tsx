import { useState, useEffect } from 'react';
import axios from 'axios';
import OrderForm from './OrderForm';
import './Cart.css';

interface CartItem {
  id: number;
  pizza: {
    id: number;
    name: string;
    price: number;
    image: string;
  };
  quantity: number;
}

const Cart = () => {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [showOrderForm, setShowOrderForm] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCartItems();
  }, []);

  const fetchCartItems = async () => {
    try {
      const response = await axios.get('/api/cart/');
      setCartItems(response.data);
    } catch (err) {
      setError('Ошибка при загрузке корзины');
    }
  };

  const updateQuantity = async (itemId: number, newQuantity: number) => {
    if (newQuantity < 1) return;

    try {
      await axios.patch(`/api/cart/${itemId}/`, { quantity: newQuantity });
      fetchCartItems();
    } catch (err) {
      setError('Ошибка при обновлении количества');
    }
  };

  const removeItem = async (itemId: number) => {
    try {
      await axios.delete(`/api/cart/${itemId}/`);
      fetchCartItems();
    } catch (err) {
      setError('Ошибка при удалении товара');
    }
  };

  const handleOrderComplete = () => {
    setShowOrderForm(false);
    setCartItems([]);
  };

  const totalPrice = cartItems.reduce((sum, item) => sum + item.pizza.price * item.quantity, 0);

  if (showOrderForm) {
    return <OrderForm cartItems={cartItems} onOrderComplete={handleOrderComplete} />;
  }

  return (
    <div className="cart">
      <h2>Корзина</h2>
      {error && <div className="error-message">{error}</div>}
      
      {cartItems.length === 0 ? (
        <p>Корзина пуста</p>
      ) : (
        <>
          <div className="cart-items">
            {cartItems.map((item) => (
              <div key={item.id} className="cart-item">
                <img src={item.pizza.image} alt={item.pizza.name} className="pizza-image" />
                <div className="item-details">
                  <h3>{item.pizza.name}</h3>
                  <p className="price">{item.pizza.price} ₽</p>
                  <div className="quantity-controls">
                    <button onClick={() => updateQuantity(item.id, item.quantity - 1)}>-</button>
                    <span>{item.quantity}</span>
                    <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>+</button>
                  </div>
                </div>
                <button className="remove-button" onClick={() => removeItem(item.id)}>
                  Удалить
                </button>
              </div>
            ))}
          </div>
          
          <div className="cart-summary">
            <div className="total">
              <span>Итого:</span>
              <span>{totalPrice} ₽</span>
            </div>
            <button className="order-button" onClick={() => setShowOrderForm(true)}>
              Оформить заказ
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default Cart; 