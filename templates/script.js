document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById('container');
    const registerBtn = document.getElementById('register');
    const loginBtn = document.getElementById('login');

    registerBtn.addEventListener('click', () => container.classList.add("active"));
    loginBtn.addEventListener('click', () => container.classList.remove("active"));
});

// ✅ **Signup Function**
function togglePassword(fieldId, icon) {
    let passwordField = document.getElementById(fieldId);
    if (passwordField.type === "password") {
        passwordField.type = "text";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    } else {
        passwordField.type = "password";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    }
}
