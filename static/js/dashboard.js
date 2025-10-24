document.addEventListener('DOMContentLoaded', function() {
    // Диаграмма распределения смен по неделе
    const weeklyShiftCtx = document.getElementById('weeklyShiftChart').getContext('2d');
    const weeklyShiftChart = new Chart(weeklyShiftCtx, {
        type: 'bar',
        data: {
            labels: ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'],
            datasets: [{
                label: 'Количество смен',
                data: [0, 0, 0, 0, 0, 0, 0], // Будет заполнено через AJAX
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Количество смен'
                    }
                }
            }
        }
    });

    // Диаграмма распределения персонала по складам
    const warehouseStaffCtx = document.getElementById('warehouseStaffChart').getContext('2d');
    const warehouseStaffChart = new Chart(warehouseStaffCtx, {
        type: 'pie',
        data: {
            labels: [], // Будет заполнено через AJAX
            datasets: [{
                data: [], // Будет заполнено через AJAX
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(199, 199, 199, 0.7)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(199, 199, 199, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: 'Распределение персонала по складам'
                }
            }
        }
    });

    // Прогноз грузоперевозок
    const cargoForecastCtx = document.getElementById('cargoForecastChart').getContext('2d');
    const cargoForecastChart = new Chart(cargoForecastCtx, {
        type: 'bar',
        data: {
            labels: ['Сегодня', 'Завтра', 'Послезавтра'],
            datasets: [
                {
                    label: 'Вес груза (тонн)',
                    data: [15, 45, 20], // Симулированные данные - сегодня нормально, завтра пик
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Требуемый персонал',
                    data: [12, 36, 16],
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Текущий персонал',
                    data: [15, 16, 15],
                    backgroundColor: 'rgba(255, 206, 86, 0.7)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Количество'
                    }
                }
            }
        }
    });

    // Создаем простой календарь на текущую неделю
    function generateCalendar() {
        const calendarDiv = document.getElementById('calendar');
        if (!calendarDiv) return;

        // Получаем информацию о текущей дате
        const now = new Date();
        const currentDay = now.getDay(); // 0 = воскресенье, 1 = понедельник, и т.д.
        
        // Корректируем, чтобы понедельник был первым днем
        const mondayOffset = currentDay === 0 ? -6 : 1 - currentDay;
        const monday = new Date(now);
        monday.setDate(now.getDate() + mondayOffset);
        
        // Создаем структуру календаря
        const calendarHtml = `
            <div class="calendar-header">
                <h5>Неделя с ${monday.toLocaleDateString('ru-RU', { month: 'long', day: 'numeric', year: 'numeric' })}</h5>
            </div>
            <div class="calendar-grid">
                <div class="calendar-row calendar-days">
                    <div class="calendar-cell">Понедельник</div>
                    <div class="calendar-cell">Вторник</div>
                    <div class="calendar-cell">Среда</div>
                    <div class="calendar-cell">Четверг</div>
                    <div class="calendar-cell">Пятница</div>
                    <div class="calendar-cell">Суббота</div>
                    <div class="calendar-cell">Воскресенье</div>
                </div>
                <div class="calendar-row" id="calendar-content">
                    <div class="calendar-cell" id="day-monday"><div class="day-content"></div></div>
                    <div class="calendar-cell" id="day-tuesday"><div class="day-content"></div></div>
                    <div class="calendar-cell" id="day-wednesday"><div class="day-content"></div></div>
                    <div class="calendar-cell" id="day-thursday"><div class="day-content"></div></div>
                    <div class="calendar-cell" id="day-friday"><div class="day-content"></div></div>
                    <div class="calendar-cell" id="day-saturday"><div class="day-content"></div></div>
                    <div class="calendar-cell" id="day-sunday"><div class="day-content"></div></div>
                </div>
            </div>
        `;
        
        calendarDiv.innerHTML = calendarHtml;
    }
    
    // Инициализация календаря
    generateCalendar();

    // Создаем визуализацию распределения персонала для сравнения до/после
    function createWarehouseStaffingVisualization(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        let html = '<table class="table table-bordered">';
        html += '<thead><tr><th>Склад</th><th>Текущий персонал</th><th>Требуемый персонал</th><th>Статус</th></tr></thead>';
        html += '<tbody>';
        
        data.forEach(warehouse => {
            const status = warehouse.currentStaff >= warehouse.requiredStaff 
                ? 'bg-success text-white' 
                : 'bg-danger text-white';
            const statusText = warehouse.currentStaff >= warehouse.requiredStaff 
                ? 'Достаточно' 
                : 'Не хватает';
                
            html += `<tr>
                <td>${warehouse.name}</td>
                <td>${warehouse.currentStaff}</td>
                <td>${warehouse.requiredStaff}</td>
                <td class="${status}">${statusText}</td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        container.innerHTML = html;
    }

    // Тестовые данные для состояния до оптимизации
    const beforeOptimizationData = [
        { name: 'Северный склад', currentStaff: 15, requiredStaff: 12 },
        { name: 'Южный склад', currentStaff: 12, requiredStaff: 10 },
        { name: 'Восточный склад', currentStaff: 8, requiredStaff: 8 },
        { name: 'Западный склад', currentStaff: 16, requiredStaff: 36 }  // Недостаточно персонала для завтрашнего пика
    ];

    // Тестовые данные для состояния после оптимизации
    const afterOptimizationData = [
        { name: 'Северный склад', currentStaff: 10, requiredStaff: 12 },
        { name: 'Южный склад', currentStaff: 10, requiredStaff: 10 },
        { name: 'Восточный склад', currentStaff: 8, requiredStaff: 8 },
        { name: 'Западный склад', currentStaff: 36, requiredStaff: 36 }  // Теперь достаточно персонала
    ];

    // Обрабатываем нажатие кнопки оптимизации
    document.getElementById('runOptimization').addEventListener('click', function() {
        // Показываем состояние загрузки
        const optimizationStatus = document.getElementById('optimizationStatus');
        optimizationStatus.className = 'alert alert-warning';
        optimizationStatus.textContent = 'Выполняется оптимизация... Пожалуйста, подождите.';
        
        // Симулируем API-запрос с помощью setTimeout
        setTimeout(function() {
            // Обновляем статус
            optimizationStatus.className = 'alert alert-success';
            optimizationStatus.textContent = 'Оптимизация завершена! Персонал перераспределен для обеспечения прогнозируемого объема грузоперевозок на завтра.';
            
            // Показываем сравнение
            document.getElementById('optimizationResults').classList.remove('d-none');
            
            // Создаем визуализации
            createWarehouseStaffingVisualization('beforeOptimization', beforeOptimizationData);
            createWarehouseStaffingVisualization('afterOptimization', afterOptimizationData);
            
            // Обновляем распределение персонала на диаграмме для визуального эффекта
            warehouseStaffChart.data.datasets[0].data = [10, 10, 8, 36]; // Скорректированные данные персонала
            warehouseStaffChart.update();
            
            // Обновляем данные персонала в диаграмме прогноза грузоперевозок
            cargoForecastChart.data.datasets[2].data = [15, 36, 15]; // Скорректированные данные персонала
            cargoForecastChart.update();
            
        }, 2000); // 2 секунды задержки для симуляции обработки
    });

    // Загружаем данные для диаграмм - используем неаутентифицированный конечный пункт для демонстрации
    fetch('/api/stats.json')
        .then(response => {
            console.log("API Response:", response);
            if (!response.ok) {
                throw new Error('Ошибка сети');
            }
            return response.json();
        })
        .then(data => {
            console.log("Dashboard data received:", data);
            // Обновляем еженедельную диаграмму смен
            if (data.shifts_by_day) {
                weeklyShiftChart.data.datasets[0].data = [
                    data.shifts_by_day.monday || 0,
                    data.shifts_by_day.tuesday || 0,
                    data.shifts_by_day.wednesday || 0,
                    data.shifts_by_day.thursday || 0,
                    data.shifts_by_day.friday || 0,
                    data.shifts_by_day.saturday || 0,
                    data.shifts_by_day.sunday || 0
                ];
                weeklyShiftChart.update();
                
                // Также обновляем календарь с количеством смен
                const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
                days.forEach(day => {
                    const dayElement = document.getElementById(`day-${day}`);
                    if (dayElement) {
                        const dayContent = dayElement.querySelector('.day-content');
                        const shiftCount = data.shifts_by_day[day] || 0;
                        
                        // Добавляем цветовой индикатор в зависимости от количества смен
                        let countClass = 'low-shifts';
                        if (shiftCount > 10) {
                            countClass = 'high-shifts';
                        } else if (shiftCount > 5) {
                            countClass = 'medium-shifts';
                        }
                        
                        dayContent.innerHTML = `
                            <div class="shift-count ${countClass}">${shiftCount}</div>
                            <div class="shift-label">Смен</div>
                        `;
                    }
                });
            }

            // Обновляем диаграмму распределения персонала по складам
            if (data.staff_by_warehouse) {
                const labels = [];
                const staffCounts = [];

                for (const warehouse in data.staff_by_warehouse) {
                    labels.push(warehouse);
                    staffCounts.push(data.staff_by_warehouse[warehouse]);
                }

                warehouseStaffChart.data.labels = labels;
                warehouseStaffChart.data.datasets[0].data = staffCounts;
                warehouseStaffChart.update();
                
                // Также инициализируем визуализацию до оптимизации с реальными данными
                if (labels.length > 0) {
                    let realBeforeData = labels.map((name, index) => {
                        // Генерируем требуемый персонал, который имеет смысл для текущего количества персонала
                        const currentStaff = staffCounts[index];
                        // Для последнего склада делаем недостаточное количество персонала на завтра
                        const requiredStaff = index === labels.length - 1 ? 
                            currentStaff * 2 : // Удваиваем для последнего склада, чтобы показать необходимость оптимизации
                            Math.max(5, currentStaff - 2); // Немного меньше, чем текущее количество для остальных
                        
                        return {
                            name: name,
                            currentStaff: currentStaff,
                            requiredStaff: requiredStaff
                        };
                    });
                    
                    // Обновляем наши тестовые данные реальными данными, если они доступны
                    if (realBeforeData.length > 0) {
                        beforeOptimizationData.length = 0;
                        realBeforeData.forEach(item => beforeOptimizationData.push(item));
                        
                        // Также обновляем данные после оптимизации, чтобы отразить изменения из реальных данных
                        afterOptimizationData.length = 0;
                        realBeforeData.forEach(item => {
                            const afterItem = {...item};
                            if (item.currentStaff < item.requiredStaff) {
                                // Для складов с недостаточным персоналом устанавливаем текущий равным требуемому после оптимизации
                                afterItem.currentStaff = item.requiredStaff;
                            } else if (item.currentStaff > item.requiredStaff + 2) {
                                // Для складов с избыточным персоналом уменьшаем персонал для баланса
                                afterItem.currentStaff = item.requiredStaff;
                            }
                            afterOptimizationData.push(afterItem);
                        });
                    }
                }
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки данных для диаграмм:', error);
            document.getElementById('weeklyShiftChart').closest('.card-body').innerHTML = 
                '<div class="alert alert-danger">Ошибка загрузки данных. Пожалуйста, попробуйте позже.</div>';
            document.getElementById('warehouseStaffChart').closest('.card-body').innerHTML = 
                '<div class="alert alert-danger">Ошибка загрузки данных. Пожалуйста, попробуйте позже.</div>';
        });
}); 