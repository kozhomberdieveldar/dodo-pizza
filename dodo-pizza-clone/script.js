// API endpoints
const API_URL = 'http://localhost:8000';

// Cart state
let cart = {
    items: [],
    total: 0
};

// DOM Elements
const cartButton = document.querySelector('.btn-cart');
const cartModal = document.createElement('div');
cartModal.className = 'cart-modal';
document.body.appendChild(cartModal);

// Initialize the application
async function init() {
    try {
        const pizzas = await fetchPizzas();
        updatePizzaCards(pizzas);
        updateCart();
    } catch (error) {
        console.error('Error initializing app:', error);
    }
}

// Fetch pizzas from API
async function fetchPizzas() {
    const response = await fetch(`${API_URL}/pizzas`);
    if (!response.ok) {
        throw new Error('Failed to fetch pizzas');
    }
    return await response.json();
}

// Update pizza cards with data from API
function updatePizzaCards(pizzas) {
    const productGrid = document.querySelector('.product-grid');
    productGrid.innerHTML = pizzas.map(pizza => `
        <div class="product-card" data-pizza-id="${pizza.id}">
            <img src="${pizza.image}" alt="${pizza.name}">
            <h3>${pizza.name}</h3>
            <p>${pizza.description}</p>
            <div class="product-footer">
                <div class="price">от ${pizza.price} ₽</div>
                <button class="btn btn-order" onclick="addToCart(${pizza.id})">Выбрать</button>
            </div>
        </div>
    `).join('');
}

// Add pizza to cart
async function addToCart(pizzaId) {
    try {
        const response = await fetch(`${API_URL}/cart/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                pizza_id: pizzaId,
                quantity: 1
            })
        });

        if (!response.ok) {
            throw new Error('Failed to add to cart');
        }

        const result = await response.json();
        updateCart();
        showNotification('Пицца добавлена в корзину!');
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('Ошибка при добавлении в корзину', true);
    }
}

// Update cart display
async function updateCart() {
    try {
        const response = await fetch(`${API_URL}/cart`);
        if (!response.ok) {
            throw new Error('Failed to fetch cart');
        }
        const cartData = await response.json();
        cart = cartData;
        
        // Update cart button
        const cartTotal = document.querySelector('.btn-cart span');
        cartTotal.textContent = `${cart.total} ₽`;

        // Update cart modal
        updateCartModal();
    } catch (error) {
        console.error('Error updating cart:', error);
    }
}

// Update cart modal
function updateCartModal() {
    cartModal.innerHTML = `
        <div class="cart-content">
            <h3>Корзина</h3>
            ${cart.items.length === 0 ? '<p>Корзина пуста</p>' : ''}
            ${cart.items.map(item => `
                <div class="cart-item">
                    <img src="${item.pizza.image}" alt="${item.pizza.name}">
                    <div class="cart-item-details">
                        <h4>${item.pizza.name}</h4>
                        <p>${item.quantity} шт. × ${item.pizza.price} ₽</p>
                    </div>
                    <div class="cart-item-total">
                        ${item.subtotal} ₽
                    </div>
                </div>
            `).join('')}
            ${cart.items.length > 0 ? `
                <div class="cart-total">
                    <span>Итого:</span>
                    <span>${cart.total} ₽</span>
                </div>
                <button class="btn btn-primary" onclick="checkout()">Оформить заказ</button>
                <button class="btn btn-secondary" onclick="clearCart()">Очистить корзину</button>
            ` : ''}
        </div>
    `;
}

// Show/hide cart modal
cartButton.addEventListener('click', () => {
    cartModal.classList.toggle('active');
});

// Close cart modal when clicking outside
document.addEventListener('click', (e) => {
    if (!cartModal.contains(e.target) && !cartButton.contains(e.target)) {
        cartModal.classList.remove('active');
    }
});

// Clear cart
async function clearCart() {
    try {
        const response = await fetch(`${API_URL}/cart/clear`, {
            method: 'POST'
        });
        if (!response.ok) {
            throw new Error('Failed to clear cart');
        }
        updateCart();
        showNotification('Корзина очищена');
    } catch (error) {
        console.error('Error clearing cart:', error);
        showNotification('Ошибка при очистке корзины', true);
    }
}

// Checkout
async function checkout() {
    // Here you would typically implement the checkout process
    showNotification('Заказ оформлен! Спасибо за покупку!');
    await clearCart();
}

// Show notification
function showNotification(message, isError = false) {
    const notification = document.createElement('div');
    notification.className = `notification ${isError ? 'error' : 'success'}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Authentication functions
function showLoginModal() {
    document.getElementById('loginModal').classList.add('active');
}

function showRegisterModal() {
    document.getElementById('registerModal').classList.add('active');
}

function hideModals() {
    document.getElementById('loginModal').classList.remove('active');
    document.getElementById('registerModal').classList.remove('active');
}

// Close modals when clicking outside
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        hideModals();
    }
});

async function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const username = form.querySelector('input[type="text"]').value;
    const password = form.querySelector('input[type="password"]').value;

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            throw new Error('Login failed');
        }

        const result = await response.json();
        showNotification('Успешный вход!');
        hideModals();
        // Here you would typically store the user's session
    } catch (error) {
        console.error('Login error:', error);
        showNotification('Ошибка входа. Проверьте учетные данные.', true);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const username = form.querySelector('input[type="text"]').value;
    const password = form.querySelector('input[type="password"]').value;
    const confirmPassword = form.querySelectorAll('input[type="password"]')[1].value;

    if (password !== confirmPassword) {
        showNotification('Пароли не совпадают', true);
        return;
    }

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            throw new Error('Registration failed');
        }

        const result = await response.json();
        showNotification('Регистрация успешна! Теперь вы можете войти.');
        hideModals();
        showLoginModal();
    } catch (error) {
        console.error('Registration error:', error);
        showNotification('Ошибка регистрации. Возможно, пользователь уже существует.', true);
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', init); 