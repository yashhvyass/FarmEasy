// Initialize AOS (Animate on Scroll) - Unchanged
document.addEventListener('DOMContentLoaded', function() {
    AOS.init({
        duration: 1000,
        once: true
    });
});

// Add smooth scrolling for anchor links - Unchanged
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Handle CTA button clicks - Unchanged
document.querySelectorAll('.cta-button').forEach(button => {
    button.addEventListener('click', function() {
        console.log('CTA button clicked');
    });
});

// New code: Hide navbar on scroll down, show on scroll up
let lastScrollPosition = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScrollPosition = window.pageYOffset;
    
    // Check if scrolling down
    if (currentScrollPosition > lastScrollPosition) {
        navbar.style.transform = 'translateY(-100%)'; // Hide navbar
    } else {
        navbar.style.transform = 'translateY(0)'; // Show navbar
    }})
