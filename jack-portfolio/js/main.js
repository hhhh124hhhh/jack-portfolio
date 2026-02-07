// Main JavaScript for jack portfolio

// =====================
// CONFIGURATION
// =====================
const CONFIG = {
    colors: {
        bgPrimary: '#0a0e17',
        bgSecondary: '#111827',
        bgTertiary: '#1f2937',
        accentPrimary: '#3b82f6',
        accentSecondary: '#8b5cf6',
        accentGlow: 'rgba(59, 130, 246, 0.3)',
        textPrimary: '#f9fafb',
        textSecondary: '#d1d5db',
        textMuted: '#6b7280',
        borderColor: '#374151'
    },
    particles: {
        count: 30,
        size: { min: 1, max: 3 },
        speed: { min: 0.5, max: 1.5 }
    },
    animation: {
        typingSpeed: 3.5,
        numberIncrement: 50
    }
};

// =====================
// UTILITIES
// =====================
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

const createElement = (tag, className, innerHTML) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (innerHTML) el.innerHTML = innerHTML;
    return el;
};

// =====================
// SCROLL PROGRESS
// =====================
function initScrollProgress() {
    const scrollProgress = $('#scroll-progress');
    if (!scrollProgress) return;

    window.addEventListener('scroll', () => {
        const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const progress = (scrollTop / scrollHeight) * 100;
        scrollProgress.style.width = `${progress}%`;
    });
}

// =====================
// CURSOR GLOW
// =====================
function initCursorGlow() {
    const cursorGlow = $('#cursor-glow');
    if (!cursorGlow) return;

    document.addEventListener('mousemove', (e) => {
        cursorGlow.style.transform = `translate(${e.clientX - 100}px, ${e.clientY - 100}px)`;
    });
}

// =====================
// PARTICLE BACKGROUND
// =====================
function initParticles() {
    const canvas = $('#particles');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];

    for (let i = 0; i < CONFIG.particles.count; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * (CONFIG.particles.size.max - CONFIG.particles.size.min) + CONFIG.particles.size.min,
            speedX: Math.random() * 2 * CONFIG.particles.speed.max - CONFIG.particles.speed.max,
            speedY: Math.random() * 2 * CONFIG.particles.speed.max - CONFIG.particles.speed.max
        });
    }

    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(particle => {
            particle.x += particle.speedX;
            particle.y += particle.speedY;

            if (particle.x < 0) particle.x = canvas.width;
            if (particle.x > canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = canvas.height;
            if (particle.y > canvas.height) particle.y = 0;

            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(59, 130, 246, 0.3)';
            ctx.fill();
        });

        requestAnimationFrame(animateParticles);
    }

    animateParticles();

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// =====================
// COUNT UP ANIMATION
// =====================
function initCountUp() {
    const countUps = $$('.count-up');

    countUps.forEach(element => {
        const finalValue = element.textContent;
        const numbers = finalValue.match(/\d+/);
        if (!numbers) return;

        const target = parseInt(numbers[0]);
        let current = 0;
        const increment = target / CONFIG.animation.numberIncrement;

        const interval = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(interval);
            }

            let displayValue = Math.floor(current).toString();
            if (finalValue.includes('K')) {
                displayValue += 'K+';
            } else if (finalValue.includes('+')) {
                displayValue += '+';
            }
            element.textContent = displayValue;
        }, 30);
    });
}

// =====================
// SKILL BARS
// =====================
function initSkillBars() {
    const skillBars = $$('.skill-bar-fill');

    skillBars.forEach(bar => {
        setTimeout(() => {
            bar.classList.add('animated');
        }, 500);
    });
}

// =====================
// GITHUB CONTRIBUTION GRID
// =====================
function initContributionGrid() {
    const grid = $('#contribution-grid');
    if (!grid) return;

    for (let i = 0; i < 364; i++) {
        const cell = createElement('div', `contribution-cell contribution-${Math.floor(Math.random() * 5) + 1}`);
        grid.appendChild(cell);
    }
}

// =====================
// REVEAL ANIMATION
// =====================
function initReveal() {
    const reveals = $$('.reveal');

    reveals.forEach(element => {
        const windowHeight = window.innerHeight;
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;

        if (elementTop < windowHeight - elementVisible) {
            element.classList.add('active');
        }
    });
}

// =====================
// SMOOTH SCROLL
// =====================
function initSmoothScroll() {
    $$('.nav-links a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = $(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// =====================
// PARALLAX SCROLL
// =====================
function initParallaxScroll() {
    const hero = $('.hero');
    if (!hero) return;

    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        hero.style.transform = `translateY(${scrolled * 0.3}px)`;
    });
}

// =====================
// INITIALIZATION
// =====================
window.addEventListener('load', () => {
    initScrollProgress();
    initCursorGlow();
    initParticles();
    initCountUp();
    initSkillBars();
    initContributionGrid();
    initReveal();
    initSmoothScroll();
    initParallaxScroll();
});

window.addEventListener('scroll', initReveal);
