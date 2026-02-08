// Efek border navbar saat scroll
const nav = document.getElementById('mainNav');
window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
        nav.style.borderColor = '#e2e8f0';
    } else {
          nav.style.borderColor = '#f1f5f9';
        }
    });
