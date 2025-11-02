document.addEventListener("DOMContentLoaded", function() {
    // Gestion de la modale d'authentification
    const userBtn = document.getElementById('user-btn');
    const closeBtn = document.getElementById('close-user-menu');
    const showRegister = document.getElementById('show-register');
    const showLogin = document.getElementById('show-login');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const authDialog = document.getElementById('auth-dialog'); // Changé de overlay à dialog
    const emailInput = document.getElementById('new_email');
    const createBtn = document.getElementById('create-btn');
    const registerError = document.getElementById('register-error');
    const loginError = document.getElementById('login-error');

    if (userBtn) userBtn.onclick = function() {
        if (authDialog) authDialog.showModal(); // Utilise la méthode showModal()
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    };

    if (closeBtn) closeBtn.onclick = function() {
        if (authDialog) authDialog.close(); // Utilise la méthode close()
    };

    // Ferme le dialogue si on clique en dehors
    if (authDialog) {
        authDialog.addEventListener('click', function(event) {
            if (event.target === authDialog) {
                authDialog.close();
            }
        });
    }

    if (showRegister) showRegister.onclick = function() {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
    };
    if (showLogin) showLogin.onclick = function() {
        registerForm.style.display = 'none';
        loginForm.style.display = 'block';
    };

    // Formulaire d'inscription
    let emailTouched = false;
    let confirmTouched = false;

    if (emailInput) {
        emailInput.addEventListener('input', function() {
            emailTouched = true;
            updateRegisterError();
        });
    }
    const confirmInput = document.getElementById('register-form').querySelector('input[name="confirm_password"]');
    if (confirmInput) {
        confirmInput.addEventListener('input', function() {
            confirmTouched = true;
            updateRegisterError();
        });
    }

    function updateRegisterError() {
        let errorMsg = "";
        const strictEmail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
        if (emailTouched && !strictEmail.test(emailInput.value)) {
            errorMsg += "Adresse mail invalide.<br>";
            createBtn.disabled = true;
            emailInput.classList.add('input-error');
        } else {
            emailInput.classList.remove('input-error');
        }
        const pwd = document.getElementById('register-form').new_password.value;
        const confirm = confirmInput.value;
        if (confirmTouched && pwd !== confirm) {
            errorMsg += "Les mots de passe ne correspondent pas.";
            createBtn.disabled = true;
            confirmInput.classList.add('input-error');
        } else {
            confirmInput.classList.remove('input-error');
        }
        if (
            strictEmail.test(emailInput.value) &&
            pwd === confirm &&
            pwd.length > 0 &&
            confirm.length > 0
        ) {
            createBtn.disabled = false;
        }
        registerError.innerHTML = errorMsg;
    }

    if (registerForm) registerForm.onsubmit = function(e) {
        e.preventDefault();
        updateRegisterError();
        if (createBtn.disabled) return;
        registerError.textContent = "";
        const pwd = this.new_password.value;
        const confirm = this.confirm_password.value;
        if (pwd !== confirm) {
            registerError.textContent = "Les mots de passe ne correspondent pas.";
            return;
        }
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

    // Formulaire de connexion
    if (loginForm) loginForm.onsubmit = function(e) {
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

    // Déconnexion
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.onclick = function() {
            fetch('/logout')
                .then (r => r.json())
                .then(data => {
                    if(data.success) {
                        location.reload();
                    }
                });
        };
    }
});
