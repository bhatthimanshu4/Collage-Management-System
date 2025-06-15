const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
    // console.log(container.classList);
})
loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
    // console.log(container.classList);
})
document.getElementById("login").addEventListener("click", function () {
    fetch("http://127.0.0.1:5001/run-menu")  // Flask API Call
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error("Error:", error));
});
