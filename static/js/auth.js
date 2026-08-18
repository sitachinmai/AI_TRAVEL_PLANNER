// Client-side Authentication & 5-Digit OTP Handlers
document.addEventListener('DOMContentLoaded', () => {

    function showAlert(msg, isError) {
        const alertEl = document.getElementById('auth-alert');
        if (!alertEl) return;
        if (!msg) {
            alertEl.classList.add('hidden');
            return;
        }
        alertEl.textContent = msg;
        alertEl.className = isError ? 'alert alert-error' : 'alert alert-success';
        alertEl.classList.remove('hidden');
    }

    function showProfileAlert(msg, isError) {
        const alertEl = document.getElementById('profile-alert');
        if (!alertEl) return;
        if (!msg) {
            alertEl.classList.add('hidden');
            return;
        }
        alertEl.textContent = msg;
        alertEl.className = isError ? 'alert alert-error' : 'alert alert-success';
        alertEl.classList.remove('hidden');
    }

    // 1. Registration Handler
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            showAlert('', false);

            const fullName = document.getElementById('full_name').value.trim();
            const email = document.getElementById('email').value.trim();
            const mobileNumber = document.getElementById('mobile_number') ? document.getElementById('mobile_number').value.trim() : '';
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;

            if (password !== confirmPassword) {
                showAlert('Passwords do not match.', true);
                return;
            }

            try {
                const response = await fetch('/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        full_name: fullName,
                        email: email,
                        mobile_number: mobileNumber,
                        password: password,
                        confirm_password: confirmPassword
                    })
                });

                const data = await response.json();
                if (!response.ok) {
                    showAlert(data.detail || 'Registration failed.', true);
                    return;
                }

                showAlert('Account created! 5-digit Email and Mobile OTPs have been sent/logged. Redirecting to email verification...', false);
                setTimeout(() => {
                    window.location.href = `/verify-otp?email=${encodeURIComponent(email)}&mobile=${encodeURIComponent(mobileNumber)}`;
                }, 1500);
            } catch (err) {
                showAlert('Network error. Please try again.', true);
            }
        });
    }

    // 2. Email OTP Verification Form Handler
    const otpForm = document.getElementById('otp-form');
    if (otpForm) {
        otpForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            showAlert('', false);

            const email = document.getElementById('email').value.trim();
            const otpDigits = Array.from(document.querySelectorAll('.otp-digit')).map(input => input.value).join('');

            if (otpDigits.length !== 5) {
                showAlert('Please enter all 5 digits of your verification code.', true);
                return;
            }

            try {
                const response = await fetch('/auth/verify-email-otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email, otp: otpDigits })
                });

                const data = await response.json();
                if (!response.ok) {
                    showAlert(data.detail || 'Invalid or expired OTP code.', true);
                    return;
                }

                // Check URL params for mobile parameter to proceed to mobile verification
                const urlParams = new URLSearchParams(window.location.search);
                const mobileParam = urlParams.get('mobile');

                if (mobileParam) {
                    showAlert('Email verified! Redirecting to Mobile OTP verification...', false);
                    setTimeout(() => {
                        window.location.href = `/verify-mobile-otp?mobile=${encodeURIComponent(mobileParam)}`;
                    }, 1500);
                } else {
                    showAlert('Email verified successfully! ✅ Redirecting to login...', false);
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 1500);
                }
            } catch (err) {
                showAlert('Network error. Please try again.', true);
            }
        });
    }

    // 3. Resend Email OTP Button Handler
    const resendBtn = document.getElementById('resend-otp-btn');
    if (resendBtn) {
        resendBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            showAlert('', false);

            const emailInput = document.getElementById('email');
            const email = emailInput ? emailInput.value.trim() : '';
            if (!email) {
                showAlert('Please provide your account email address.', true);
                return;
            }

            try {
                const response = await fetch('/auth/resend-verification-otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email })
                });

                const data = await response.json();
                if (!response.ok) {
                    showAlert(data.detail || 'Could not resend OTP.', true);
                    return;
                }

                showAlert('A new 5-digit verification code has been sent to your email (or data/dev_emails.log).', false);
            } catch (err) {
                showAlert('Network error. Please try again.', true);
            }
        });
    }

    // 4. Login Handler
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            showAlert('', false);

            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/auth/login/json', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email, password: password })
                });

                const data = await response.json();
                if (!response.ok) {
                    if (response.status === 403) {
                        const detailMsg = data.detail || '';
                        if (detailMsg.toLowerCase().includes('mobile')) {
                            showAlert('Your mobile number is not verified yet. Redirecting to mobile verification page...', true);
                            setTimeout(() => {
                                window.location.href = `/verify-mobile-otp?email=${encodeURIComponent(email)}`;
                            }, 2000);
                        } else {
                            showAlert('Your email is not verified yet. Redirecting to verification page...', true);
                            setTimeout(() => {
                                window.location.href = `/verify-otp?email=${encodeURIComponent(email)}`;
                            }, 2000);
                        }
                    } else {
                        showAlert(data.detail || 'Invalid email or password.', true);
                    }
                    return;
                }

                localStorage.setItem('access_token', data.access_token);
                window.location.href = '/dashboard';
            } catch (err) {
                showAlert('Network error. Please try again.', true);
            }
        });
    }

    // 5. Profile Form Handler
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            showProfileAlert('', false);

            const fullName = document.getElementById('full_name').value.trim();
            const mobileNumber = document.getElementById('mobile_number') ? document.getElementById('mobile_number').value.trim() : '';
            const travelStyle = document.getElementById('travel_style').value;
            const foodPref = document.getElementById('food_preference').value;
            const budgetPref = document.getElementById('budget_preference').value;
            const interests = document.getElementById('interests').value.trim();

            const token = localStorage.getItem('access_token');
            try {
                const response = await fetch('/auth/profile', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': token ? `Bearer ${token}` : ''
                    },
                    body: JSON.stringify({
                        full_name: fullName,
                        mobile_number: mobileNumber,
                        travel_style: travelStyle,
                        food_preference: foodPref,
                        budget_preference: budgetPref,
                        interests: interests
                    })
                });

                const data = await response.json();
                if (!response.ok) {
                    showProfileAlert(data.detail || 'Profile update failed.', true);
                    return;
                }

                showProfileAlert('Profile & preferences updated successfully! ✅', false);
            } catch (err) {
                showProfileAlert('Network error updating profile.', true);
            }
        });
    }
});
