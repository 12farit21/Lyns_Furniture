/**
 * Lyn's Furniture Miami - Main JavaScript
 */

// ─── Image Placeholder (global, capture phase — covers all <img> including modal) ──
(function () {
    var svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">',
          '<defs>',
            '<linearGradient id="lfbg" x1="0" y1="0" x2="1" y2="1">',
              '<stop offset="0%" stop-color="#EFF6FF"/>',
              '<stop offset="100%" stop-color="#E0E7FF"/>',
            '</linearGradient>',
          '</defs>',
          /* background */
          '<rect width="400" height="400" fill="url(#lfbg)"/>',
          /* decorative circles */
          '<circle cx="40" cy="40" r="65" fill="#DBEAFE" opacity="0.5"/>',
          '<circle cx="360" cy="360" r="80" fill="#E0E7FF" opacity="0.5"/>',
          /* back cushions */
          '<rect x="92" y="148" width="93" height="70" rx="14" fill="#BFDBFE"/>',
          '<rect x="195" y="148" width="93" height="70" rx="14" fill="#C7D2FE"/>',
          /* seat */
          '<rect x="86" y="208" width="228" height="58" rx="10" fill="#93C5FD"/>',
          /* armrests */
          '<rect x="62" y="163" width="36" height="83" rx="14" fill="#A5B4FC"/>',
          '<rect x="302" y="163" width="36" height="83" rx="14" fill="#A5B4FC"/>',
          /* base strip */
          '<rect x="86" y="261" width="228" height="13" rx="4" fill="#7DD3FC"/>',
          /* legs */
          '<rect x="106" y="272" width="12" height="26" rx="4" fill="#6366F1"/>',
          '<rect x="158" y="272" width="12" height="26" rx="4" fill="#6366F1"/>',
          '<rect x="230" y="272" width="12" height="26" rx="4" fill="#6366F1"/>',
          '<rect x="282" y="272" width="12" height="26" rx="4" fill="#6366F1"/>',
          /* label */
          '<text x="200" y="338" text-anchor="middle" font-family="system-ui,sans-serif"',
          ' font-size="13" fill="#94A3B8" letter-spacing="2.5" font-weight="500">NO IMAGE</text>',
        '</svg>'
    ].join('');

    var PLACEHOLDER = 'data:image/svg+xml,' + encodeURIComponent(svg);

    function applyPlaceholder(img) {
        if (img.src === PLACEHOLDER || img.dataset.placeholder === '1') return;
        img.dataset.placeholder = '1';
        img.onerror = null;
        img.src = PLACEHOLDER;
    }

    /* capture phase — catches errors from ALL img elements, including dynamic ones */
    document.addEventListener('error', function (e) {
        if (e.target && e.target.tagName === 'IMG') {
            applyPlaceholder(e.target);
        }
    }, true);
}());


document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                e.preventDefault();
                const target = document.querySelector(targetId);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });

    // Add to Cart buttons (home page + product list)
    document.querySelectorAll('.add-to-cart-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            addToCart(this.dataset.productId, this);
        });
    });
});

// ─── Cart Badge ────────────────────────────────────────────────────────────────

function updateCartBadge(count) {
    const badge = document.getElementById('cart-badge');
    if (!badge) return;
    if (count > 0) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

// ─── Add to Cart ───────────────────────────────────────────────────────────────

function addToCart(productId, btn) {
    const originalHTML = btn ? btn.innerHTML : '';

    fetch('/cart/add/' + productId + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: 'quantity=1'
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.status === 'success') {
            updateCartBadge(data.cart_total_items);
            if (btn) {
                btn.innerHTML = '<svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Added!';
                btn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
                btn.classList.add('bg-green-600');
                setTimeout(function() {
                    btn.innerHTML = originalHTML;
                    btn.classList.remove('bg-green-600');
                    btn.classList.add('bg-blue-600', 'hover:bg-blue-700');
                }, 2000);
            }
        } else {
            alert(data.message || 'Could not add to cart.');
        }
    })
    .catch(function() {
        alert('Network error. Please try again.');
    });
}

// ─── Cookie Helper ─────────────────────────────────────────────────────────────

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
