// Подставляет текущий год в подвал (без JavaScript остаётся год сервера).
const yearElement = document.getElementById("current-year");

if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
}
