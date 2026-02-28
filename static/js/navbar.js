document.addEventListener('DOMContentLoaded', function() {
    const userBtn = document.getElementById('user-btn');
    const userDialog = document.getElementById('user-menu-dialog');
    const closeBtns = userDialog?.querySelectorAll('.close-modal, [data-close-modal]');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const showRegister = document.getElementById('show-register');
    const showLogin = document.getElementById('show-login');
    const loginError = document.getElementById('login-error');
    const registerError = document.getElementById('register-error');
    const logoutBtn = document.getElementById('logout-btn');
    const languageSelect = document.getElementById('language-select');
    const languageForm = document.getElementById('language-form');

    const newEmail = document.getElementById('new_email');
    const newPassword = document.querySelector('input[name="new_password"]');
    const confirmPassword = document.querySelector('input[name="confirm_password"]');
    const createBtn = document.getElementById('create-btn');

    function validateRegisterForm() {
        if (!newEmail || !newPassword || !confirmPassword || !createBtn) return;
        const emailValid = newEmail.value.includes('@');
        const passwordsMatch = newPassword.value === confirmPassword.value && newPassword.value !== '';
        createBtn.disabled = !(emailValid && passwordsMatch);
    }

    if (newEmail) newEmail.addEventListener('input', validateRegisterForm);
    if (newPassword) newPassword.addEventListener('input', validateRegisterForm);
    if (confirmPassword) confirmPassword.addEventListener('input', validateRegisterForm);

    if (userBtn && userDialog) {
        userBtn.addEventListener('click', () => {
            userDialog.removeAttribute('hidden');
            userDialog.showModal();
        });
    }

    if (closeBtns && userDialog) {
        closeBtns.forEach(btn => btn.addEventListener('click', () => {
            userDialog.close();
            userDialog.setAttribute('hidden', '');
        }));
    }

    if (showRegister) {
        showRegister.addEventListener('click', () => {
            loginForm.style.display = 'none';
            registerForm.style.display = 'block';
        });
    }

    if (showLogin) {
        showLogin.addEventListener('click', () => {
            registerForm.style.display = 'none';
            loginForm.style.display = 'block';
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            fetch('/login', {
                method: 'POST',
                body: formData
            }).then(r => r.json()).then(data => {
                if(data.success) {
                    location.reload();
                } else {
                    loginError.textContent = data.error;
                    loginForm.querySelectorAll('input').forEach(input => input.classList.add('input-error'));
                }
            }).catch(err => {
                console.error('Login error:', err);
                loginError.textContent = 'Une erreur est survenue lors de la connexion.';
            });
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(registerForm);
            fetch('/register', {
                method: 'POST',
                body: formData
            }).then(r => r.json()).then(data => {
                if(data.success) {
                    location.reload();
                } else {
                    registerError.textContent = data.error;
                    registerForm.querySelectorAll('input').forEach(input => input.classList.add('input-error'));
                }
            }).catch(err => {
                console.error('Registration error:', err);
                registerError.textContent = 'Une erreur est survenue lors de l\'inscription.';
            });
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            // Using GET as per backend implementation
            fetch('/logout')
            .then(() => location.reload());
        });
    }

    if (languageSelect && languageForm) {
        languageSelect.addEventListener('change', () => {
            languageForm.submit();
        });
    }

    // Close when clicking outside the dialog content
    if (userDialog) {
        userDialog.addEventListener('click', (event) => {
            if (event.target === userDialog) {
                userDialog.close();
                userDialog.setAttribute('hidden', '');
            }
        });
    }
});
