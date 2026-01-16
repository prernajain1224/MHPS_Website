// MHPS Website - Main JavaScript with Bootstrap

document.addEventListener('DOMContentLoaded', function() {
    
    // Active nav link highlighting
    highlightActiveNavLink();
    
    // Smooth scroll for anchor links
    initSmoothScroll();
    
    // Mobile menu auto-close on link click
    initMobileMenuAutoClose();
});

// Highlight active navigation link
function highlightActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath !== '/' && href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Smooth scroll for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Close mobile menu if open
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                    bootstrap.Collapse.getInstance(navbarCollapse).hide();
                }
            }
        });
    });
}

// Auto-close mobile menu when clicking a link
function initMobileMenuAutoClose() {
    const navLinks = document.querySelectorAll('.nav-link');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (!navbarCollapse) return;
    
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 768 && navbarCollapse.classList.contains('show')) {
                bootstrap.Collapse.getInstance(navbarCollapse).hide();
            }
        });
    });
}

// Utility function to show loading spinner (for future use)
function showLoader() {
    const loader = document.createElement('div');
    loader.id = 'page-loader';
    loader.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    loader.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:9999;';
    document.body.appendChild(loader);
}

function hideLoader() {
    const loader = document.getElementById('page-loader');
    if (loader) loader.remove();
}