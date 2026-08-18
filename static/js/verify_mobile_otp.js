// Client-side Mobile 5-Digit OTP Handlers
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

    // Auto-focus movement and paste handler for 5-digit OTP
    const otpInputs = document.querySelectorAll('.otp-digit');
    otpInputs.forEach((input, index) => {
        input.addEventListener('input', (e) => {
            if (e.target.value.length === 1 && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && !e.target.value && index > 0) {
                otpInputs[index - 1].focus();
            }
        });

        input.addEventListener('paste', (e) => {
            e.preventDefault();
            const pasted = (e.clipboardData || window.clipboardData).getData('text').trim();
            if (/^\d{5}$/.test(pasted)) {
                pasted.split('').forEach((char, i) => {
                    if (otpInputs[i]) otpInputs[i].value = char;
                });
                otpInputs[4].focus();
            }
        });
    });

    // 10-Minute Countdown Timer
    let timeLeft = 600;
    const timerDisplay = document.getElementById('timer-display');
    if (timerDisplay) {
        const timerInterval = setInterval(() => {
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                timerDisplay.textContent = 'Expired';
                timerDisplay.style.color = '#991b1b';
                return;
            }
            timeLeft--;
            const mins = Math.floor(timeLeft / 60);
            const secs = timeLeft % 60;
            timerDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }, 1000);
    }

    // Mobile OTP Form Submit Handler
    const mobileForm = document.getElementById('mobile-otp-form');
    if (mobileForm) {
        mobileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            showAlert('', false);

            const mobileNumber = document.getElementById('mobile_number').value.trim();
            const otpDigits = Array.from(document.querySelectorAll('.otp-digit')).map(input => input.value).join('');

            if (otpDigits.length !== 5) {
                showAlert('Please enter all 5 digits of your mobile verification code.', true);
                return;
            }

            try {
                const response = await fetch('/auth/verify-mobile-otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mobile_number: mobileNumber, otp: otpDigits })
                });

                const data = await response.json();
                if (!response.ok) {
                    showAlert(data.detail || 'Invalid or expired Mobile OTP.', true);
                    return;
                }

                showAlert('Mobile number verified successfully! ✅ Redirecting to login...', false);
                setTimeout(() => {
                    window.location.href = '/login';
                }, 1500);
            } catch (err) {
                showAlert('Network error. Please try again.', true);
            }
        });
    }

    // Resend Mobile OTP Button Handler
    const resendBtn = document.getElementById('resend-mobile-otp-btn');
    if (resendBtn) {
        resendBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            showAlert('', false);

            const mobileInput = document.getElementById('mobile_number');
            const mobileNumber = mobileInput ? mobileInput.value.trim() : '';

            if (!mobileNumber) {
                showAlert('Please enter your mobile number.', true);
                return;
            }

            try {
                const response = await fetch('/auth/resend-mobile-otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mobile_number: mobileNumber })
                });

                const data = await response.json();
                if (!response.ok) {
                    showAlert(data.detail || 'Could not resend Mobile OTP.', true);
                    return;
                }

                showAlert('A new 5-digit Mobile OTP was generated (data/dev_mobile_otps.log).', false);
            } catch (err) {
                showAlert('Network error. Please try again.', true);
            }
        });
    }
});
