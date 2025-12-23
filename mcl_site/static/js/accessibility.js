document.addEventListener('DOMContentLoaded', function () {
    const accessBtn = document.createElement('button');
    accessBtn.innerHTML = '👁️';
    accessBtn.className = 'btn btn-dark position-fixed bottom-0 end-0 m-4 rounded-circle shadow-lg';
    accessBtn.style.zIndex = '1000';
    accessBtn.style.width = '50px';
    accessBtn.style.height = '50px';
    accessBtn.setAttribute('aria-label', 'Налаштування доступності');

    document.body.appendChild(accessBtn);

    let isHighContrast = false;
    let isLargeText = false;

    accessBtn.addEventListener('click', function () {
        // Toggle High Contrast
        if (!isHighContrast) {
            document.body.classList.add('high-contrast');
            document.documentElement.style.filter = 'contrast(120%)';
            isHighContrast = true;
        } else {
            document.body.classList.remove('high-contrast');
            document.documentElement.style.filter = 'none';
            isHighContrast = false;
        }
    });

    // Add High Contrast Styles
    const style = document.createElement('style');
    style.innerHTML = `
        .high-contrast {
            background-color: #000 !important;
            color: #fff !important;
        }
        .high-contrast a {
            color: #ffff00 !important;
            text-decoration: underline !important;
        }
        .high-contrast .card {
            background-color: #333 !important;
            border: 1px solid #fff !important;
            color: #fff !important;
        }
        .high-contrast .navbar {
            background-color: #000 !important;
            border-bottom: 2px solid #fff !important;
        }
        .high-contrast .nav-link {
            color: #fff !important;
        }
    `;
    document.head.appendChild(style);
});
