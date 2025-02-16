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