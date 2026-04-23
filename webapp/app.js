const tg = window.Telegram.WebApp;
tg.expand();

const products = [
    { id: "Pechini 1", name: "Taplyonniy", price: 45000, img: "assets/podium_1.png" },
    { id: "Pechini 2", name: "Yubileyniy", price: 45000, img: "assets/podium_2.png" },
    { id: "Pechini 3", name: "Yulduz", price: 48000, img: "assets/podium_3.png" },
    { id: "Pechini 4", name: "Olmali", price: 60000, img: "assets/podium_4.png" },
    { id: "Pechini 5", name: "Pop Corn", price: 60000, img: "assets/podium_5.png" },
    { id: "Pechini 6", name: "Azbuka", price: 70000, img: "assets/podium_6.png" }
];

let cart = {};
let outOfStock = [];

window.onload = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const stockParam = urlParams.get('out_of_stock');
    console.log("RAW param:", stockParam); 
    if (stockParam) {
        outOfStock = stockParam.split(',').map(id => decodeURIComponent(id));
    }
    console.log("outOfStock array:", outOfStock);
    console.log("products ids:", products.map(p => p.id));

    // Load saved data
    const savedName = localStorage.getItem('bakery_name');
    const savedPhone = localStorage.getItem('bakery_phone');
    const savedStore = localStorage.getItem('bakery_store');
    if (savedName) document.getElementById('userName').value = savedName;
    if (savedPhone) document.getElementById('userPhone').value = savedPhone;
    if (savedStore) document.getElementById('userStore').value = savedStore;

    renderSlider();
    renderProducts();
    startAutoSlide();

    setTimeout(() => {
        document.getElementById('loader').style.opacity = '0';
        setTimeout(() => document.getElementById('loader').classList.add('hidden'), 500);
    }, 800);
};

function renderSlider() {
    const slider = document.getElementById('topSlider');
    slider.innerHTML = '';
    products.forEach(p => {
        const isOut = outOfStock.includes(p.id);
        const slide = document.createElement('div');
        slide.className = `slide-item ${isOut ? 'out-of-stock' : ''}`;
        slide.innerHTML = `
            <div class="slide-title-outer">${p.name}</div>
            <div class="slide-image-wrapper">
                <img src="${p.img}" alt="${p.name}">
            </div>
        `;
        slider.appendChild(slide);
    });
}

function renderProducts() {
    const grid = document.getElementById('productGrid');
    grid.innerHTML = '';

    products.forEach(p => {
        const isOut = outOfStock.includes(p.id);
        const card = document.createElement('div');
        card.className = `product-card ${isOut ? 'out-of-stock' : ''}`;
        
        card.innerHTML = `
            <div class="img-container">
                <img src="${p.img}" alt="${p.name}">
            </div>
            <div class="product-info">
                <h3>${p.name}</h3>
                <p class="price">${p.price.toLocaleString()} so'm</p>
                <div class="qty-control">
                    ${isOut ? `
                        <span style="color: #ff4d4d; font-weight: 800; font-size: 13px;">Hozircha yo'q</span>
                    ` : (cart[p.id] ? `
                        <button class="qty-btn" onclick="updateQty('${p.id}', -1)">-</button>
                        <span>${cart[p.id]}</span>
                        <button class="qty-btn" onclick="updateQty('${p.id}', 1)">+</button>
                    ` : `
                        <button class="premium-btn" onclick="updateQty('${p.id}', 1)" style="width:100%; padding: 6px;">Qo'shish</button>
                    `)}
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

function updateQty(id, delta) {
    cart[id] = (cart[id] || 0) + delta;
    if (cart[id] <= 0) delete cart[id];
    updateCartUI();
    renderProducts();
    try { tg.HapticFeedback.impactOccurred('light'); } catch(e){}
}

function updateCartUI() {
    const cartBar = document.getElementById('cartBar');
    const countSpan = document.getElementById('cartCount');
    const totalSpan = document.getElementById('cartTotal');
    
    let totalItems = 0;
    let totalPrice = 0;
    for (const id in cart) {
        const p = products.find(prod => prod.id === id);
        totalItems += cart[id];
        totalPrice += p.price * cart[id];
    }
    
    if (totalItems > 0) {
        cartBar.classList.remove('hidden');
        countSpan.innerText = `${totalItems} dona mahsulot`;
        totalSpan.innerText = `${totalPrice.toLocaleString()} so'm`;
    } else {
        cartBar.classList.add('hidden');
    }
}

// Auto Slide
let slideInterval;
function autoSlide() {
    const slider = document.getElementById('topSlider');
    if (!slider) return;
    const slideWidth = slider.querySelector('.slide-item').offsetWidth + 16;
    if (slider.scrollLeft + slider.clientWidth >= slider.scrollWidth - 10) {
        slider.scrollTo({ left: 0, behavior: 'smooth' });
    } else {
        slider.scrollBy({ left: slideWidth, behavior: 'smooth' });
    }
}
function startAutoSlide() {
    clearInterval(slideInterval);
    slideInterval = setInterval(autoSlide, 3000);
}

// Modal
const modal = document.getElementById('orderModal');
document.getElementById('orderBtn').onclick = () => {
    renderCartItems();
    modal.classList.remove('hidden');
};
document.getElementById('closeModal').onclick = () => modal.classList.add('hidden');

function renderCartItems() {
    const container = document.getElementById('cartItems');
    container.innerHTML = '';
    for (const id in cart) {
        const p = products.find(prod => prod.id === id);
        container.innerHTML += `
            <div style="display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid #eee; padding-bottom:5px;">
                <span>${p.name} x ${cart[id]}</span>
                <span>${(p.price * cart[id]).toLocaleString()} so'm</span>
            </div>
        `;
    }
}

document.getElementById('submitOrder').onclick = () => {
    const name = document.getElementById('userName').value;
    const phone = document.getElementById('userPhone').value;
    const store = document.getElementById('userStore').value;

    if (!name || !phone || !store) {
        alert("Iltimos, barcha maydonlarni to'ldiring!");
        return;
    }

    localStorage.setItem('bakery_name', name);
    localStorage.setItem('bakery_phone', phone);
    localStorage.setItem('bakery_store', store);

    navigator.geolocation.getCurrentPosition(
        (pos) => sendOrder(pos.coords.latitude, pos.coords.longitude, name, phone, store),
        () => sendOrder(0, 0, name, phone, store),
        { timeout: 5000 }
    );
};

function sendOrder(lat, lon, name, phone, store) {
    const orderData = { cart, name, phone, store, lat, lon };
    tg.sendData(JSON.stringify(orderData));
}
