document.addEventListener("DOMContentLoaded", function() {
  const emailInput = document.getElementById('profile_email');
  const pwdInput = document.getElementById('password');
  const pwdConfirmInput = document.getElementById('password_confirm');
  const submitBtn = document.getElementById('profile-submit');
  const errorDiv = document.getElementById('profile-error');
  const form = document.getElementById('profile-form');

  let emailTouched = false;
  let pwdTouched = false;
  let pwdConfirmTouched = false;

  function updateProfileError() {
    let errorMsg = "";
    const strictEmail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

    // Vérification email
    if (emailTouched) {
      if (!strictEmail.test(emailInput.value)) {
        errorMsg += "Adresse mail invalide.<br>";
        emailInput.classList.add('input-error');
      } else {
        emailInput.classList.remove('input-error');
      }
    } else {
      emailInput.classList.remove('input-error');
    }

    // Vérification mot de passe
    const pwd = pwdInput.value;
    const confirm = pwdConfirmInput.value;
    if ((pwdTouched || pwdConfirmTouched) && (pwd || confirm)) {
      if (pwd !== confirm) {
        errorMsg += "Les mots de passe ne correspondent pas.";
        pwdConfirmInput.classList.add('input-error');
      } else {
        pwdConfirmInput.classList.remove('input-error');
      }
    } else {
      pwdConfirmInput.classList.remove('input-error');
    }

    // Désactive le bouton si erreur
    if (
      (emailTouched && !strictEmail.test(emailInput.value)) ||
      ((pwdTouched || pwdConfirmTouched) && pwd !== confirm)
    ) {
      submitBtn.disabled = true;
    } else {
      submitBtn.disabled = false;
    }

    errorDiv.innerHTML = errorMsg;
  }

  emailInput.addEventListener('input', function() {
    emailTouched = true;
    updateProfileError();
  });
  pwdInput.addEventListener('input', function() {
    pwdTouched = true;
    updateProfileError();
  });
  pwdConfirmInput.addEventListener('input', function() {
    pwdConfirmTouched = true;
    updateProfileError();
  });

  form.onsubmit = function(e) {
    updateProfileError();
    if (submitBtn.disabled) {
      e.preventDefault();
    }
  };

  // Pas de check initial pour ne rien afficher tant que l'utilisateur n'a rien fait
});
