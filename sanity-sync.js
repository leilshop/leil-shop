// sanity-sync.js - مزامنة منتجات Sanity تلقائياً مع صفحات المتجر
const SANITY_PROJECT_ID = 'ouygoq48';
const SANITY_DATASET = 'production';

async function fetchSanityProduct() {
  // 1. قراءة اسم المنتج المكتوب أصلاً في الـ h1 بالصفحة
  const titleEl = document.querySelector('.product-details h1');
  if (!titleEl) return;
  const productName = titleEl.innerText.trim();

  // 2. البحث عن المنتج في Sanity بالاسم المطابق
  const query = encodeURIComponent(`*[_type == "product" && title == "${productName}"][0]`);
  const url = `https://${SANITY_PROJECT_ID}.api.sanity.io/v2021-10-21/data/query/${SANITY_DATASET}?query=${query}`;

  try {
    const response = await fetch(url, { cache: 'no-store' });
    const data = await response.json();
    const product = data.result;

    if (!product) {
      console.warn(`Product "${productName}" not found in Sanity.`);
      return;
    }

    // تحديث المتغير العام باسم المنتج للسلة
    if (typeof currentProductName !== 'undefined') {
      currentProductName = product.title;
    }

    // تحديث السلوجن والوصف
    const sloganEl = document.querySelector('.product-details .slogan');
    if (sloganEl && product.slogan) sloganEl.innerText = product.slogan;

    const descEl = document.querySelector('.product-desc p');
    if (descEl && product.description) descEl.innerText = product.description;

    // تحديث أزرار المقاسات والأسعار والمخزون
    if (product.sizes && product.sizes.length > 0) {
      const sizeContainer = document.querySelector('.size-selector');
      if (sizeContainer) {
        sizeContainer.innerHTML = '';

        product.sizes.forEach((item, index) => {
          const btn = document.createElement('button');
          const isPinky = item.size && item.size.includes('Pinky');
          btn.className = isPinky ? 'pinky-btn' : 'size-btn';

          btn.innerText = item.size;
          btn.setAttribute('data-price', item.price);
          btn.setAttribute('data-old', item.originalPrice || '');

          // فحص حالة المخزون
          const isAvailable = item.inStock !== false && (item.quantity === undefined || item.quantity > 0);
          btn.setAttribute('data-instock', isAvailable);

          if (!isAvailable) {
            btn.classList.add('out-of-stock');
          }

          // عند الضغط على الحجم
          btn.onclick = function () {
            if (typeof selectSize === 'function') {
              selectSize(this, item.size, isPinky ? 4 : 0);
            }
          };

          sizeContainer.appendChild(btn);

          // تفعيل أول حجم تلقائياً عند فتح الصفحة
          if (index === 0 && typeof selectSize === 'function') {
            selectSize(btn, item.size, isPinky ? 4 : 0);
          }
        });
      }
    }
  } catch (error) {
    console.error('Error fetching data from Sanity:', error);
  }
}

window.addEventListener('DOMContentLoaded', fetchSanityProduct);