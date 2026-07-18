

// فرمت‌دهی عدد قیمت با جداکننده‌ی هزارگان (مشابه فرمتی که قالب‌های فارسی معمولاً استفاده می‌کنن)
// اگه واحد پول یا فرمت دیگه‌ای لازم داری (مثلاً اضافه کردن "تومان" یا اعداد فارسی) همینجا تغییرش بده
function formatPrice(value) {
    const number = Number(value);
    if (isNaN(number)) return value;
    const formatted = number.toLocaleString("en-US", { maximumFractionDigits: 0 });
    return `${formatted} تومان`;
}

function increaseQuantity(productId, stock) {
    const quantitySpan = document.getElementById(`quantity-${productId}`);
    const currentQuantity = parseInt(quantitySpan.innerText.trim());

    if (currentQuantity >= stock) {
        showToast("موجودی کافی نیست", "error");
        return;
    }
    changeProductQuantity(productId, currentQuantity + 1);
}

function decreaseQuantity(productId) {
    const quantitySpan = document.getElementById(`quantity-${productId}`);
    const currentQuantity = parseInt(quantitySpan.innerText.trim());

    if (currentQuantity <= 1) {
        showToast("حداقل تعداد ۱ است", "error");
        return;
    }
    changeProductQuantity(productId, currentQuantity - 1);
}

function changeProductQuantity(productId, quantity) {

    const url = `/cart/update/${productId}/`;

    fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {

        if (data.success) {

            // تغییر عدد وسط
            document.getElementById(`quantity-${productId}`).innerText = quantity;

            // آپدیت قیمت این آیتم (دسکتاپ و موبایل) با فرمت درست
            if (data.item_total !== undefined) {
                const formatted = formatPrice(data.item_total);
                const desktopPrice = document.getElementById(`item-total-${productId}`);
                const mobilePrice = document.getElementById(`item-total-mobile-${productId}`);
                if (desktopPrice) desktopPrice.innerText = formatted;
                if (mobilePrice) mobilePrice.innerText = formatted;
            }

            // آپدیت جمع کل سبد با فرمت درست
            if (data.cart_total_price !== undefined) {
                const totalPriceEl = document.getElementById("cart-total-price");
                if (totalPriceEl) totalPriceEl.innerText = formatPrice(data.cart_total_price);
            }

            // آپدیت تعداد کل موارد سبد (بالای صفحه)
            if (data.total_quantity !== undefined) {
                const totalQuantityEl = document.getElementById("total-quantity");
                if (totalQuantityEl) totalQuantityEl.innerText = data.total_quantity;
            }

            // آپدیت تعداد کل سبد (بج هدر سایت)
            const cartCount = document.getElementById("cart-count");
            if (cartCount) {
                cartCount.innerText = data.cart_count;
            }

            showToast(data.message, "success");

        } else {
            showToast(data.error, "error");
        }

    })
    .catch(error => {
        console.log(error);
        showToast("خطایی رخ داد", "error");
    });
}

function removeProduct(productId) {

    const url = `/cart/remove/${productId}/`;

    fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        }
    })
    .then(response => response.json())
    .then(data => {

        if (data.success) {

            // حذف کامل ردیف محصول از DOM
            const item = document.getElementById(`cart-item-${productId}`);
            if (item) item.remove();

            // اگر سبد خالی شد پیام مناسب نمایش داده شود
            const list = document.getElementById("cart-items-list");
            if (list && list.children.length === 0) {
                list.innerHTML = `<div class="row text-center" id="empty-cart-message"><p> محصولی برای نمایش وجود ندارد</p></div>`;
            }

            const cartCount = document.getElementById("cart-count");
            if (cartCount) {
                cartCount.innerText = data.cart_count;
            }

            if (data.total_quantity !== undefined) {
                const totalQuantityEl = document.getElementById("total-quantity");
                if (totalQuantityEl) totalQuantityEl.innerText = data.total_quantity;
            }

            if (data.cart_total_price !== undefined) {
                const totalPriceEl = document.getElementById("cart-total-price");
                if (totalPriceEl) totalPriceEl.innerText = formatPrice(data.cart_total_price);
            }

            showToast(data.message, "success");

        } else {
            showToast(data.error, "error");
        }

    })
    .catch(error => {
        console.log(error);
        showToast("خطایی رخ داد", "error");
    });
}
