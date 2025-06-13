import { useState } from 'react';
import axios from 'axios';

interface OrderFormProps {
  cartItems: any[];
  onOrderComplete: () => void;
}

const OrderForm = ({ cartItems, onOrderComplete }: OrderFormProps) => {
  const [address, setAddress] = useState('');
  const [phone, setPhone] = useState('');
  const [comment, setComment] = useState('');
  const [promoCode, setPromoCode] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const response = await axios.post('/api/orders/create/', {
        cart_item_ids: cartItems.map(item => item.id),
        address,
        phone,
        comment,
        promo_code: promoCode
      });

      if (response.status === 201) {
        onOrderComplete();
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Произошла ошибка при создании заказа');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="order-form">
      <h2>Оформление заказа</h2>
      
      {error && <div className="error-message">{error}</div>}

      <div className="form-group">
        <label htmlFor="address">Адрес доставки:</label>
        <input
          type="text"
          id="address"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="phone">Телефон:</label>
        <input
          type="tel"
          id="phone"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="promoCode">Промокод (если есть):</label>
        <input
          type="text"
          id="promoCode"
          value={promoCode}
          onChange={(e) => setPromoCode(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label htmlFor="comment">Комментарий к заказу:</label>
        <textarea
          id="comment"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />
      </div>

      <button type="submit" className="submit-button">
        Оформить заказ
      </button>
    </form>
  );
};

export default OrderForm; 