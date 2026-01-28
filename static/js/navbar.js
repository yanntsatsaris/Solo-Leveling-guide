document.addEventListener("DOMContentLoaded", function() {
    // Selectors
    const userBtn = document.getElementById('user-btn');
    const closeBtn = document.getElementById('close-user-menu');
    const showRegister = document.getElementById('show-register');
    const showLogin = document.getElementById('show-login');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const userDialog = document.getElementById('user-menu-dialog');
    const emailInput = document.getElementById('new_email');
    const createBtn = document.getElementById('create-btn');
    const registerError = document.getElementById('register-error');
    const loginError = document.getElementById('login-error');
    const logoutBtn = document.getElementById('logout-btn');

    // Modal display/hide
    if (userBtn && userDialog) {
        userBtn.onclick = function() {
            userDialog.showModal();
            loginForm.style.display = 'block';
            registerForm.style.display = 'none';
        };
    }
    if (closeBtn && userDialog) {
        closeBtn.onclick = function() {
            userDialog.close();
        };
    }
    // Close on backdrop click
    if (userDialog) {
        userDialog.addEventListener('click', (event) => {
            if (event.target === userDialog) {
                userDialog.close();
            }
        });
    }

    if (showRegister) {
        showRegister.onclick = function() {
            loginForm.style.display = 'none';
            registerForm.style.display = 'block';
        };
    }
    if (showLogin) {
        showLogin.onclick = function() {
            registerForm.style.display = 'none';
            loginForm.style.display = 'block';
        };
    }

    // Registration validation
    let emailTouched = false;
    let confirmTouched = false;

    if (emailInput) {
        emailInput.addEventListener('input', function() {
            emailTouched = true;
            updateRegisterError();
        });
    }

    const confirmInput = registerForm ? registerForm.querySelector('input[name="confirm_password"]') : null;
    if (confirmInput) {
        confirmInput.addEventListener('input', function() {
            confirmTouched = true;
            updateRegisterError();
        });
    }

    function updateRegisterError() {
        let errorMsg = "";
        const strictEmail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
        if (emailInput && emailTouched && !strictEmail.test(emailInput.value)) {
            errorMsg += "Adresse mail invalide.<br>";
            createBtn.disabled = true;
            emailInput.classList.add('input-error');
        } else if (emailInput) {
            emailInput.classList.remove('input-error');
        }

        const pwd = registerForm ? registerForm.new_password.value : "";
        const confirm = confirmInput ? confirmInput.value : "";
        if (confirmInput && confirmTouched && pwd !== confirm) {
            errorMsg += "Les mots de passe ne correspondent pas.";
            createBtn.disabled = true;
            confirmInput.classList.add('input-error');
        } else if (confirmInput) {
            confirmInput.classList.remove('input-error');
        }

        if (
            emailInput && strictEmail.test(emailInput.value) &&
            pwd === confirm &&
            pwd.length > 0 &&
            confirm.length > 0
        ) {
            createBtn.disabled = false;
        }
        if (registerError) registerError.innerHTML = errorMsg;
    }

    // Submit Registration
    if (registerForm) {
        registerForm.onsubmit = function(e) {
            e.preventDefault();
            updateRegisterError();
            if (createBtn.disabled) return;
            registerError.textContent = "";
            fetch('/register', {
                method: 'POST',
                body: new FormData(this)
            }).then(r => r.json()).then(data => {
                if(data.success) {
                    location.reload();
                } else {
                    registerError.textContent = data.error;
                    registerForm.style.display = 'block';
                }
            });
        };
    }

    // Submit Login
    if (loginForm) {
        loginForm.onsubmit = function(e) {
            e.preventDefault();
            loginError.textContent = "";
            fetch('/login', {
                method: 'POST',
                body: new FormData(this)
            }).then(r => r.json()).then(data => {
                if(data.success) {
                    location.reload();
                } else {
                    loginError.textContent = data.error;
                    loginForm.style.display = 'block';
                }
            });
        };
    }

    // Logout
    if (logoutBtn) {
        logoutBtn.onclick = function() {
            fetch('/logout')
                .then(r => r.json())
                .then(data => {
                    if(data.success) {
                        location.reload();
                    }
                });
        };
    }
});
