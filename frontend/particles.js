// ============================================
// ANIMATED PARTICLE BACKGROUND SYSTEM
// Lightweight floating particles with subtle connections
// Matches the cyan/violet theme of Invoice-IQ
// ============================================

(function initParticles() {
    const canvas = document.getElementById('particles-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;
    let mouseX = -1000;
    let mouseY = -1000;

    // Configuration
    const DARK_COLORS = [
        'rgba(6, 182, 212,',    // cyan
        'rgba(139, 92, 246,',   // violet
        'rgba(244, 114, 182,',  // pink
        'rgba(56, 189, 248,',   // light blue
    ];

    const LIGHT_COLORS = [
        'rgba(8, 145, 178,',    // darker cyan
        'rgba(109, 40, 217,',   // darker violet
        'rgba(190, 24, 93,',    // darker pink
        'rgba(14, 116, 144,',   // teal
    ];

    function getColors() {
        const theme = document.documentElement.getAttribute('data-theme');
        return theme === 'light' ? LIGHT_COLORS : DARK_COLORS;
    }

    function getConnectionColor() {
        const theme = document.documentElement.getAttribute('data-theme');
        return theme === 'light' ? '8, 145, 178' : '6, 182, 212';
    }

    const CONFIG = {
        particleCount: 60,
        maxSpeed: 0.3,
        particleMinSize: 1,
        particleMaxSize: 2.5,
        connectionDistance: 150,
        mouseRadius: 200,
    };

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    function createParticle() {
        const colors = getColors();
        const color = colors[Math.floor(Math.random() * colors.length)];
        const theme = document.documentElement.getAttribute('data-theme');
        const baseOp = theme === 'light' ? (0.15 + Math.random() * 0.25) : (0.2 + Math.random() * 0.4);
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * CONFIG.maxSpeed * 2,
            vy: (Math.random() - 0.5) * CONFIG.maxSpeed * 2,
            size: CONFIG.particleMinSize + Math.random() * (CONFIG.particleMaxSize - CONFIG.particleMinSize),
            color: color,
            baseOpacity: baseOp,
            pulseSpeed: 0.005 + Math.random() * 0.01,
            pulseOffset: Math.random() * Math.PI * 2,
        };
    }

    function init() {
        resize();
        particles = [];
        // Scale particle count based on screen size
        const area = canvas.width * canvas.height;
        const count = Math.min(CONFIG.particleCount, Math.floor(area / 20000));
        for (let i = 0; i < count; i++) {
            particles.push(createParticle());
        }
    }

    function drawParticle(p, time) {
        const pulse = Math.sin(time * p.pulseSpeed + p.pulseOffset) * 0.15 + 0.85;
        const opacity = p.baseOpacity * pulse;
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color + opacity + ')';
        ctx.fill();

        // Subtle glow
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2);
        ctx.fillStyle = p.color + (opacity * 0.1) + ')';
        ctx.fill();
    }

    function drawConnections() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < CONFIG.connectionDistance) {
                    const opacity = (1 - dist / CONFIG.connectionDistance) * 0.08;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(${getConnectionColor()}, ${opacity})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
    }

    function updateParticle(p) {
        p.x += p.vx;
        p.y += p.vy;

        // Subtle mouse repulsion
        const dx = p.x - mouseX;
        const dy = p.y - mouseY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < CONFIG.mouseRadius && dist > 0) {
            const force = (CONFIG.mouseRadius - dist) / CONFIG.mouseRadius * 0.02;
            p.vx += (dx / dist) * force;
            p.vy += (dy / dist) * force;
        }

        // Dampen velocity
        p.vx *= 0.999;
        p.vy *= 0.999;

        // Ensure minimum speed
        const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
        if (speed < CONFIG.maxSpeed * 0.3) {
            p.vx += (Math.random() - 0.5) * 0.02;
            p.vy += (Math.random() - 0.5) * 0.02;
        }

        // Wrap around edges
        if (p.x < -50) p.x = canvas.width + 50;
        if (p.x > canvas.width + 50) p.x = -50;
        if (p.y < -50) p.y = canvas.height + 50;
        if (p.y > canvas.height + 50) p.y = -50;
    }

    function animate(time) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        drawConnections();

        for (const p of particles) {
            updateParticle(p);
            drawParticle(p, time);
        }

        animationId = requestAnimationFrame(animate);
    }

    // Event listeners
    window.addEventListener('resize', () => {
        resize();
        // Reposition any out-of-bounds particles
        for (const p of particles) {
            if (p.x > canvas.width) p.x = Math.random() * canvas.width;
            if (p.y > canvas.height) p.y = Math.random() * canvas.height;
        }
    });

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    document.addEventListener('mouseleave', () => {
        mouseX = -1000;
        mouseY = -1000;
    });

    // Reduce animation when tab is not visible
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            cancelAnimationFrame(animationId);
        } else {
            animationId = requestAnimationFrame(animate);
        }
    });

    // Listen for theme changes
    window.addEventListener('themechange', () => {
        const colors = getColors();
        const theme = document.documentElement.getAttribute('data-theme');
        for (const p of particles) {
            p.color = colors[Math.floor(Math.random() * colors.length)];
            p.baseOpacity = theme === 'light' ? (0.15 + Math.random() * 0.25) : (0.2 + Math.random() * 0.4);
        }
    });

    // Start
    init();
    animationId = requestAnimationFrame(animate);
})();
