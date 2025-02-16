// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;

// Элемент для регистрации касаний
const touchArea = document.getElementById('touch-area');

// Обработчик клика и касаний
function handleTouch(event) {
    // Получаем координаты
    let x, y;
    if (event.type === 'touchstart') {
        x = event.touches[0].clientX;
        y = event.touches[0].clientY;
    } else {
        x = event.clientX;
        y = event.clientY;
    }

    // Создаем квадратик
    const square = document.createElement('div');
    square.style.position = 'absolute';
    square.style.left = `${x - 25}px`; // Центрируем квадратик
    square.style.top = `${y - 25}px`;
    square.style.width = '50px';
    square.style.height = '50px';
    square.style.backgroundColor = 'rgba(255, 0, 0, 0.5)'; // Полупрозрачный красный
    square.style.borderRadius = '10px'; // Закругленные углы
    square.style.transition = 'transform 0.2s, opacity 0.5s'; // Анимация
    touchArea.appendChild(square);

    // Анимация появления
    setTimeout(() => {
        square.style.transform = 'scale(1.2)';
        square.style.opacity = '0';
    }, 10);

    // Удаляем квадратик через 0.5 секунды
    setTimeout(() => {
        square.remove();
    }, 500);

    // Вибрация (если поддерживается)
    if (navigator.vibrate) {
        navigator.vibrate(50); // Вибрация на 50 мс
    }

    // Отправляем данные боту через Telegram API
    tg.sendData(JSON.stringify({
        action: 'touch',
        coordinates: { x, y }
    }));
}

// Вешаем обработчики событий
touchArea.addEventListener('click', handleTouch);
touchArea.addEventListener('touchstart', handleTouch);

// Инициализация мини-приложения
tg.expand(); // Раскрываем на весь экран
tg.ready();  // Готово к работе