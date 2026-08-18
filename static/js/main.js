// Main JavaScript Module for AI Travel Planner
document.addEventListener('DOMContentLoaded', () => {
    // Bind Logout Button Handler (Guest Reset)
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                await fetch('/auth/logout', { method: 'POST' });
                localStorage.removeItem('access_token');
                window.location.href = '/dashboard';
            } catch (err) {
                console.error('Logout error:', err);
                window.location.href = '/dashboard';
            }
        });
    }
});
