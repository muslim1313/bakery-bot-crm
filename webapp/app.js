const tg = window.Telegram?.WebApp;
if (tg) {
    tg.ready();
    tg.expand();
}

let products = [];
let cart = {};
let outOfStock = [];
let isSubmitting = false;

window.onload = async () => {
    // Parse inventory constraints from URL params
    const urlParams = new URLSearchParams(window.location.search);
    const stockParam = urlParams.get('out_of_stock');
    if (stockParam) {
        outOfStock = stockParam.split(',').map(id => decodeURIComponent(id.trim()));
    }

    // Dynamic loading of products from server API or products.json, with premium fallback
    try {
        const response = await fetch('/api/products');
        if (!response.ok) throw new Error("API failed");
        products = await response.json();
    } catch (err) {
        console.log("Failed to load dynamic API, trying products.json fallback", err);
        try {
            const response = await fetch('products.json');
            const data = await response.json();
            products = data.map(p => ({
                id: p.id,
                name: p.name,
                price: p.sell,
                img: p.img
            }));
        } catch (fallbackErr) {
            console.error("Failed to load products.json, using static fallback", fallbackErr);
            products = [
                { id: "Pechini 1", name: "Taplyonniy", price: 45000, img: "assets/podium_1.png" },
                { id: "Pechini 2", name: "Yubileyniy", price: 45000, img: "assets/podium_2.png" },
                { id: "Pechini 3", name: "Yulduz", price: 48000, img: "assets/podium_3.png" },
                { id: "Pechini 4", name: "Olmali", price: 60000, img: "assets/podium_4.png" },
                { id: "Pechini 5", name: "Pop Corn", price: 60000, img: "assets/podium_5.png" },
                { id: "Pechini 6", name: "Azbuka", price: 70000, img: "assets/podium_6.png" }
            ];
        }
    }

    // Cache prefill from LocalStorage
    const savedName = localStorage.getItem('bakery_name');
    const savedPhone = localStorage.getItem('bakery_phone');
    const savedStore = localStorage.getItem('bakery_store');
    if (savedName) document.getElementById('userName').value = savedName;
    if (savedPhone) document.getElementById('userPhone').value = savedPhone;
    if (savedStore) document.getElementById('userStore').value = savedStore;

    // Premium Share Button handler (Anti-slop openTelegramLink protocol)
    const shareBtn = document.getElementById('shareBtn');
    if (shareBtn) {
        shareBtn.addEventListener('click', (event) => {
            const shareUrl = 'https://t.me/SaxovataBaraka_buyurtma_bot';
            const shareText = "Saxovat Baraka — premium artisan pishiriqlar buyurtma berish uchun bot!";
            const tgShareUrl = `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}`;
            const deepShareUrl = `tg://msg_url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}`;

            if (tg) {
                try {
                    tg.openTelegramLink(deepShareUrl);
                    event.preventDefault();
                    return;
                } catch (err) {
                    try {
                        tg.openLink(tgShareUrl);
                        event.preventDefault();
                        return;
                    } catch (fallbackErr) {
                        // fallback to default anchor navigation
                    }
                }
            }
        });
    }

    // Modal Action Bindings
    const modal = document.getElementById('orderModal');
    const orderBtn = document.getElementById('orderBtn');
    const closeModal = document.getElementById('closeModal');
    
    if (orderBtn) {
        orderBtn.onclick = () => {
            renderCartItems();
            modal.classList.remove('hidden');
            if (window.gsap) {
                window.gsap.fromTo(modal, 
                    { opacity: 0 }, 
                    { opacity: 1, duration: 0.3, ease: "power2.out" }
                );
                window.gsap.fromTo(modal.querySelector('.modal-content'),
                    { y: 50, scale: 0.95 },
                    { y: 0, scale: 1, duration: 0.5, ease: "power4.out" }
                );
            }
        };
    }
    
    if (closeModal) {
        closeModal.onclick = () => {
            if (window.gsap) {
                window.gsap.to(modal.querySelector('.modal-content'), {
                    y: 30,
                    scale: 0.95,
                    duration: 0.3,
                    ease: "power3.in"
                });
                window.gsap.to(modal, {
                    opacity: 0,
                    duration: 0.3,
                    ease: "power2.in",
                    onComplete: () => modal.classList.add('hidden')
                });
            } else {
                modal.classList.add('hidden');
            }
        };
    }

    // Submit Action
    const submitBtn = document.getElementById('submitOrder');
    if (submitBtn) {
        submitBtn.onclick = handleSubmit;
    }

    // Initial Builders
    renderProducts();

    // Stagger reveal on start
    if (window.gsap) {
        window.gsap.from('.product-card', {
            y: 30,
            opacity: 0,
            duration: 0.8,
            stagger: 0.1,
            ease: "power3.out",
            delay: 0.5
        });
    }

    // Loader removal logic (Skeletal Fade transition)
    setTimeout(() => {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.classList.add('hidden');
                document.body.classList.remove('loading-state');
            }, 500);
        }
    }, 800);
};

// Asymmetric Bento Grid Builder
function renderProducts() {
    const grid = document.getElementById('productGrid');
    if (!grid) return;
    grid.innerHTML = '';

    products.forEach(p => {
        const isOut = outOfStock.includes(p.id);

        if (isOut && cart[p.id]) {
            delete cart[p.id];
            updateCartUI();
        }

        const card = document.createElement('div');
        card.className = `product-card ${isOut ? 'out-of-stock' : ''}`;

        let controlHTML;
        if (isOut) {
            controlHTML = `<span class="out-of-stock-badge">Hozircha sotuvda yo'q</span>`;
        } else if (cart[p.id]) {
            controlHTML = `
                <div class="qty-control">
                    <button class="qty-btn" onclick="updateQty('${p.id}', -1)">−</button>
                    <span>${cart[p.id]}</span>
                    <button class="qty-btn" onclick="updateQty('${p.id}', 1)">+</button>
                </div>
            `;
        } else {
            controlHTML = `
                <button class="premium-btn" onclick="updateQty('${p.id}', 1)" style="width: 100%;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 14px; height: 14px; margin-right: 6px; display: inline-block; vertical-align: middle;"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                    Savatchaga qo'shish
                </button>
            `;
        }

        card.innerHTML = `
            <div class="img-container">
                <img src="${p.img}" alt="${p.name}">
            </div>
            <div class="product-info">
                <h3>${p.name}</h3>
                <div class="price">${p.price.toLocaleString()} so'm</div>
                <div class="action-box">${controlHTML}</div>
            </div>
        `;
        grid.appendChild(card);
    });
}

// Spring Qty Update Interface
function updateQty(id, delta) {
    if (outOfStock.includes(id)) return;

    cart[id] = (cart[id] || 0) + delta;
    if (cart[id] <= 0) delete cart[id];
    
    updateCartUI();
    renderProducts();
    
    // Tactile Spring feedback
    try {
        tg?.HapticFeedback?.impactOccurred('light');
    } catch (e) {}
}

// Flat macOS Dock/Cart Update
function updateCartUI() {
    const cartBar = document.getElementById('cartBar');
    const countSpan = document.getElementById('cartCount');
    const totalSpan = document.getElementById('cartTotal');

    let totalItems = 0;
    let totalPrice = 0;
    for (const id in cart) {
        const p = products.find(prod => prod.id === id);
        if (p) {
            totalItems += cart[id];
            totalPrice += p.price * cart[id];
        }
    }

    if (totalItems > 0) {
        const wasHidden = cartBar.classList.contains('hidden');
        cartBar.classList.remove('hidden');
        countSpan.innerText = `${totalItems} dona mahsulot`;
        totalSpan.innerText = `${totalPrice.toLocaleString()} so'm`;

        if (wasHidden && window.gsap) {
            window.gsap.fromTo(cartBar, 
                { y: 120, opacity: 0, scale: 0.9 },
                { y: 0, opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.5)" }
            );
        } else if (window.gsap) {
            // elastic pop feedback on update
            window.gsap.to(cartBar, {
                scale: 1.05,
                duration: 0.1,
                yoyo: true,
                repeat: 1,
                ease: "power2.out"
            });
        }
    } else {
        if (!cartBar.classList.contains('hidden') && window.gsap) {
            window.gsap.to(cartBar, {
                y: 120,
                opacity: 0,
                scale: 0.9,
                duration: 0.4,
                ease: "power3.in",
                onComplete: () => cartBar.classList.add('hidden')
            });
        } else {
            cartBar.classList.add('hidden');
        }
    }
}

// Modal cart contents renderer
function renderCartItems() {
    const container = document.getElementById('cartItems');
    if (!container) return;
    container.innerHTML = '';
    
    for (const id in cart) {
        const p = products.find(prod => prod.id === id);
        if (p) {
            const row = document.createElement('div');
            row.className = 'modal-item-row';
            row.innerHTML = `
                <span class="modal-item-name">${p.name} × ${cart[id]} d.</span>
                <span class="modal-item-price font-mono">${(p.price * cart[id]).toLocaleString()} so'm</span>
            `;
            container.appendChild(row);
        }
    }
}

// Form Submission & Geolocation Pipeline
function handleSubmit() {
    if (isSubmitting) return;

    const submitBtn = document.getElementById('submitOrder');
    const name = document.getElementById('userName').value.trim();
    const phone = document.getElementById('userPhone').value.trim();
    const store = document.getElementById('userStore').value.trim();

    if (Object.keys(cart).length === 0) {
        alert("Savatchangiz bo'sh. Iltimos mahsulot tanlang.");
        return;
    }

    if (!name || !phone || !store) {
        alert("Iltimos, buyurtmani rasmiylashtirish uchun barcha ma'lumotlarni to'ldiring!");
        return;
    }

    if (!tg) {
        alert("Buyurtma berish faqat Telegram ilovasi ichida ishlaydi.");
        return;
    }

    // Cache to localstorage
    localStorage.setItem('bakery_name', name);
    localStorage.setItem('bakery_phone', phone);
    localStorage.setItem('bakery_store', store);
    
    isSubmitting = true;
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = "Yuborilmoqda...";
    }

    navigator.geolocation.getCurrentPosition(
        (pos) => sendOrder(pos.coords.latitude, pos.coords.longitude, name, phone, store, submitBtn),
        () => sendOrder(0, 0, name, phone, store, submitBtn),
        { timeout: 5000 }
    );
}

function sendOrder(lat, lon, name, phone, store, submitBtn) {
    const orderData = { cart, name, phone, store, lat, lon };
    try {
        tg.sendData(JSON.stringify(orderData));
        const modal = document.getElementById('orderModal');
        if (modal) modal.classList.add('hidden');
        cart = {};
        updateCartUI();
        renderProducts();
    } finally {
        isSubmitting = false;
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerText = "Buyurtmani tasdiqlash";
        }
    }
}
