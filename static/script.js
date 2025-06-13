// API endpoints
const API_URL = 'http://localhost:8000';

// Cart state
let cart = {
    items: [],
    total: 0
};

// Current category
let currentCategory = 'pizza';

// DOM Elements
const cartButton = document.querySelector('.btn-cart');
const cartModal = document.createElement('div');
cartModal.className = 'cart-modal';
document.body.appendChild(cartModal);

// Получение CSRF-токена из cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize the application
async function init() {
    try {
        await loadCategories();
        const initialCategory = getCategoryFromUrl();
        await loadProducts(initialCategory);
        updateCart();
    } catch (error) {
        console.error('Error initializing app:', error);
    }
}

// Функция для смены категории и обновления URL
async function changeCategory(categorySlug) {
    console.log('Клик по категории:', categorySlug);
    history.pushState({}, '', `/category/${categorySlug}`);
    await loadProducts(categorySlug);
}

// Модифицируем loadCategories для использования changeCategory
async function loadCategories() {
    try {
        const response = await fetch(`${API_URL}/api/categories/`);
        if (!response.ok) {
            throw new Error('Failed to fetch categories');
        }
        const categories = await response.json();
        const navLinks = document.querySelector('.nav-links');
        if (!navLinks) {
            console.error('nav-links не найден');
            return;
        }
        navLinks.innerHTML = categories.map(cat => `
            <a href=\"#\" class=\"nav-link\" data-category=\"${cat.slug}\">${cat.name}</a>
        `).join('');
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                const category = e.target.dataset.category;
                console.log('Навигация: клик по', category);
                await changeCategory(category);
            });
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Load products by category
async function loadProducts(category) {
    try {
        console.log('Загрузка товаров для категории:', category);
        const response = await fetch(`${API_URL}/api/categories/${category}/products/`);
        if (!response.ok) {
            throw new Error('Failed to fetch products');
        }
        const products = await response.json();
        updateProductCards(products);
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

// Update product cards with data from API
function updateProductCards(products) {
    const productGrid = document.querySelector('.product-grid');
    productGrid.innerHTML = products.map(product => `
        <div class="product-card" data-product-id="${product.id}">
            <img src="${product.image}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>${product.description}</p>
            <div class="product-footer">
                <div class="price">от ${product.price} ₽</div>
                <button class="btn btn-order" onclick="addToCart(${product.id})">Выбрать</button>
            </div>
        </div>
    `).join('');
}

// Add pizza to cart
async function addToCart(pizzaId) {
    try {
        const response = await fetch(`${API_URL}/api/cart/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                pizza_id: pizzaId,
                quantity: 1
            })
        });

        if (response.status === 401 || response.status === 403) {
            showNotification('Войдите, чтобы добавить в корзину', true);
            setTimeout(() => { window.location.href = '/login/'; }, 1200);
            return;
        }
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
        const response = await fetch(`${API_URL}/cart`, {
            credentials: 'same-origin',
        });
        if (response.status === 401 || response.status === 403) {
            showNotification('Войдите, чтобы пользоваться корзиной', true);
            setTimeout(() => { window.location.href = '/login/'; }, 1200);
            return;
        }
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
                        <div class="cart-item-quantity">
                            <button class="quantity-btn" onclick="updateCartItemQuantity(${item.id}, ${item.quantity - 1})">-</button>
                            <input type="number" class="quantity-input" value="${item.quantity}" 
                                   onchange="updateCartItemQuantity(${item.id}, this.value)">
                            <button class="quantity-btn" onclick="updateCartItemQuantity(${item.id}, ${item.quantity + 1})">+</button>
                        </div>
                        <p>${item.pizza.price} ₽ за шт.</p>
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
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            credentials: 'same-origin',
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
    try {
        const response = await fetch(`${API_URL}/api/orders/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                cart: cart
            })
        });
        if (response.status === 401 || response.status === 403) {
            showNotification('Войдите, чтобы оформить заказ', true);
            setTimeout(() => { window.location.href = '/login/'; }, 1200);
            return;
        }
        if (!response.ok) {
            throw new Error('Failed to create order');
        }
        const order = await response.json();
        showNotification(`Заказ #${order.order_id} оформлен! Спасибо за покупку!`);
        await clearCart();
    } catch (error) {
        console.error('Error creating order:', error);
        showNotification('Ошибка при оформлении заказа', true);
    }
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

// Search products
async function searchProducts() {
    const query = document.getElementById('searchInput').value;
    const sortBy = document.getElementById('sortSelect').value;
    const minPrice = document.getElementById('minPrice').value;
    const maxPrice = document.getElementById('maxPrice').value;
    
    try {
        const params = new URLSearchParams({
            q: query,
            sort: sortBy
        });
        
        if (minPrice) params.append('min_price', minPrice);
        if (maxPrice) params.append('max_price', maxPrice);
        
        const response = await fetch(`${API_URL}/api/search/?${params}`);
        if (!response.ok) {
            throw new Error('Failed to search products');
        }
        
        const products = await response.json();
        updateProductCards(products);
    } catch (error) {
        console.error('Error searching products:', error);
        showNotification('Ошибка при поиске товаров', true);
    }
}

// Sort products
function sortProducts() {
    searchProducts();
}

// Filter by price
function filterByPrice() {
    searchProducts();
}

// Update cart item quantity
async function updateCartItemQuantity(itemId, quantity) {
    try {
        const response = await fetch(`${API_URL}/api/cart/update/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                item_id: itemId,
                quantity: quantity
            })
        });

        if (!response.ok) {
            throw new Error('Failed to update cart item');
        }

        const result = await response.json();
        updateCart();
        showNotification('Количество товара обновлено');
    } catch (error) {
        console.error('Error updating cart item:', error);
        showNotification('Ошибка при обновлении количества', true);
    }
}

// При загрузке страницы определяем категорию из URL
function getCategoryFromUrl() {
    const match = window.location.pathname.match(/^\/category\/([\w-]+)/);
    return match ? match[1] : 'pizza';
}

// Обработка перехода по истории браузера (назад/вперед)
window.addEventListener('popstate', async () => {
    const category = getCategoryFromUrl();
    await loadProducts(category);
});

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', init); 