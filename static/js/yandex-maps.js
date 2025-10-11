class YandexMapManager {
    constructor() {
        this.map = null;
        this.trafficLayer = null;
        this.isTrafficVisible = true;
        this.smolenskBounds = null;
        this.trafficData = {
            free: 0,
            loaded: 0,
            jams: 0,
            heavy: 0,
            segments: []
        };
        this.init();
    }

    async init() {
        await this.loadYandexMaps();
        this.initMap();
    }

    loadYandexMaps() {
        return new Promise((resolve, reject) => {
            if (window.ymaps) {
                ymaps.ready(resolve);
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://api-maps.yandex.ru/2.1/?lang=ru_RU&apikey=617caf35-de8b-4c44-a7cf-16950326f3e8';
            
            script.onload = () => ymaps.ready(resolve);
            script.onerror = reject;
            
            document.head.appendChild(script);
        });
    }

    initMap() {
        try {
            // Границы Смоленской области
            this.smolenskBounds = [
                [53.5, 31.0], // юго-запад
                [56.0, 36.0]  // северо-восток
            ];

            this.map = new ymaps.Map('map', {
                center: [54.7818, 32.0401], // Смоленск
                zoom: 10,
                controls: ['zoomControl', 'typeSelector', 'fullscreenControl']
            }, {
                restrictMapArea: [
                    [53.5, 31.0], // юго-запад
                    [56.0, 36.0]  // северо-восток
                ]
            });

            // Добавляем слой пробок через traffic.load
            this.trafficLayer = new ymaps.TrafficLayer({
                trafficJamColor: 'rgb(255, 69, 69)',
                slowTrafficColor: 'rgb(255, 165, 0)'
            });

            if (this.isTrafficVisible) {
                this.map.layers.add(this.trafficLayer);
            }

            // Добавляем маркер ЦОДД
            const marker = new ymaps.Placemark([54.7818, 32.0401], {
                balloonContent: 'ЦОДД Смоленской области<br>ул. Большая Краснофлотская, д. 70',
                hintContent: 'ЦОДД Смоленской области'
            }, {
                preset: 'islands#blueGovernmentIcon',
                iconColor: '#1e88e5'
            });

            this.map.geoObjects.add(marker);

            // Добавляем несколько светофоров в Смоленске (примерные координаты)
            this.addTrafficLights();

            // Загружаем данные о пробках
            this.updateTrafficData();

            // Обновляем данные каждые 2 минуты
            setInterval(() => {
                this.updateTrafficData();
            }, 120000);

            console.log('✅ Карта инициализирована с ограничением по Смоленской области');
        } catch (error) {
            console.error('❌ Ошибка создания карты:', error);
        }
    }

    // Добавление светофоров на карту
    addTrafficLights() {
        const trafficLights = [
            { coords: [54.7825, 32.0451], name: "Светофор ул. Ленина - ул. Октябрьской Революции" },
            { coords: [54.7792, 32.0523], name: "Светофор пр. Гагарина - ул. Николаева" },
            { coords: [54.7861, 32.0387], name: "Светофор ул. Большая Советская - ул. Дзержинского" },
            { coords: [54.7743, 32.0418], name: "Светофор ул. Кирова - ул. Багратиона" },
            { coords: [54.7889, 32.0584], name: "Светофор ул. Рыленкова - ул. Неверовского" },
            { coords: [54.7932, 32.0315], name: "Светофор Вяземское шоссе - ул. Кутузова" },
            { coords: [54.7698, 32.0287], name: "Светофор ул. Фрунзе - ул. 12 лет Октября" },
            { coords: [54.7811, 32.0652], name: "Светофор Рославльское шоссе - ул. Шевченко" },
            // Добавляем больше светофоров для лучшего покрытия
            { coords: [54.7856, 32.0498], name: "Светофор ул. Конёнкова - ул. Тенишевой" },
            { coords: [54.7764, 32.0589], name: "Светофор ул. Бакунина - ул. Кашена" },
            { coords: [54.7901, 32.0423], name: "Светофор ул. Ново-Московская - ул. Урицкого" },
            { coords: [54.7721, 32.0356], name: "Светофор ул. Попова - ул. Кловская" }
        ];

        trafficLights.forEach(light => {
            const trafficLight = new ymaps.Placemark(light.coords, {
                balloonContent: `
                    <div>
                        <strong>${light.name}</strong><br>
                        <div class="mt-2">
                            <span class="badge bg-success">● Работает</span><br>
                            <small class="text-muted">Режим: круглосуточно</small>
                        </div>
                `,
                hintContent: 'Светофор'
            }, {
                preset: 'islands#circleIcon',
                iconColor: '#ffd700',
                iconCaptionMaxWidth: '150'
            });

            this.map.geoObjects.add(trafficLight);
        });

        console.log(`✅ Добавлено ${trafficLights.length} светофоров на карту`);
    }

    // Обновление данных о пробках
    updateTrafficData() {
        if (!this.map) return;

        // Симуляция данных о пробках
        this.simulateTrafficData();
        
        // Обновляем интерфейс
        this.updateTrafficUI();
        
        // Обновляем время последнего обновления
        this.updateLastUpdateTime();
    }

    simulateTrafficData() {
        this.trafficData = {
            free: 0,
            loaded: 0,
            jams: 0,
            heavy: 0,
            segments: []
        };

        const roads = [
            { name: 'М-1 "Беларусь"', length: 120, points: 8 },
            { name: 'А-141 "Орёл-Витебск"', length: 180, points: 12 },
            { name: 'Р-120 "Орёл-Витебск"', length: 150, points: 10 },
            { name: 'Подъезд к Смоленску', length: 50, points: 6 },
            { name: 'Смоленская кольцевая', length: 40, points: 5 },
            { name: 'ул. Ленина', length: 8, points: 4 },
            { name: 'пр. Гагарина', length: 12, points: 6 },
            { name: 'ул. Большая Советская', length: 10, points: 5 }
        ];

        roads.forEach(road => {
            for (let i = 0; i < road.points; i++) {
                // Создаем более реалистичные данные о пробках
                const baseLevel = Math.random() > 0.7 ? 3 : 0; // базовая загрузка
                const randomFactor = Math.floor(Math.random() * 8);
                const jamLevel = Math.min(10, baseLevel + randomFactor);
                
                const segment = {
                    road: road.name,
                    level: jamLevel,
                    location: `Участок ${i+1}`,
                    length: Math.floor(road.length / road.points),
                    speed: Math.max(5, 60 - jamLevel * 5) // примерная скорость
                };
                this.trafficData.segments.push(segment);

                if (jamLevel <= 2) this.trafficData.free++;
                else if (jamLevel <= 5) this.trafficData.loaded++;
                else if (jamLevel <= 9) this.trafficData.jams++;
                else this.trafficData.heavy++;
            }
        });

        // Добавляем случайные события (аварии, ремонты)
        if (Math.random() > 0.7) {
            const affectedRoads = roads.filter(() => Math.random() > 0.5);
            affectedRoads.forEach(road => {
                const eventSegment = {
                    road: road.name,
                    level: 10,
                    location: `Авария/ремонт`,
                    length: 1,
                    speed: 0,
                    event: true
                };
                this.trafficData.segments.push(eventSegment);
                this.trafficData.heavy++;
            });
        }
    }

    updateTrafficUI() {
        document.getElementById('free-roads').textContent = this.trafficData.free;
        document.getElementById('loaded-roads').textContent = this.trafficData.loaded;
        document.getElementById('traffic-jams').textContent = this.trafficData.jams;
        document.getElementById('heavy-jams').textContent = this.trafficData.heavy;

        const jamList = document.getElementById('jam-list');
        jamList.innerHTML = '';

        if (this.trafficData.segments.length === 0) {
            jamList.innerHTML = '<p class="text-success">На дорогах Смоленской области пробок нет</p>';
            return;
        }

        const roads = {};
        this.trafficData.segments.forEach(segment => {
            if (!roads[segment.road]) roads[segment.road] = [];
            roads[segment.road].push(segment);
        });

        Object.keys(roads).forEach(roadName => {
            const roadSegments = roads[roadName];
            const maxJam = Math.max(...roadSegments.map(s => s.level));
            const avgJam = Math.round(roadSegments.reduce((sum, s) => sum + s.level, 0) / roadSegments.length);
            const eventSegments = roadSegments.filter(s => s.event);
            
            let statusClass = 'text-success';
            let statusText = 'Свободно';
            let badgeClass = 'bg-success';
            
            if (maxJam > 5 && maxJam <= 9) {
                statusClass = 'text-danger';
                statusText = 'Пробки';
                badgeClass = 'bg-danger';
            } else if (maxJam === 10) {
                statusClass = 'text-dark';
                statusText = 'Затор';
                badgeClass = 'bg-dark';
            } else if (maxJam > 2) {
                statusClass = 'text-warning';
                statusText = 'Загружено';
                badgeClass = 'bg-warning';
            }

            const roadElement = document.createElement('div');
            roadElement.className = 'mb-2 p-2 border rounded';
            roadElement.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <strong>${roadName}</strong>
                    <span class="badge ${badgeClass}">${statusText}</span>
                </div>
                <div class="d-flex justify-content-between align-items-center mt-1">
                    <small class="text-muted">Участков: ${roadSegments.length}</small>
                    <small class="text-muted">Макс: ${maxJam}/10</small>
                    <small class="text-muted">Сред: ${avgJam}/10</small>
                </div>
                ${eventSegments.length > 0 ? 
                    `<div class="mt-1">
                        <small class="text-danger"><i class="bi bi-exclamation-triangle"></i> Дорожные события: ${eventSegments.length}</small>
                    </div>` : ''
                }
            `;
            jamList.appendChild(roadElement);
        });
    }

    updateLastUpdateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
        document.getElementById('last-update').textContent = timeString;
    }

    toggleTrafficLayer() {
        if (!this.trafficLayer) return;

        this.isTrafficVisible = !this.isTrafficVisible;
        
        if (this.isTrafficVisible) {
            this.map.layers.add(this.trafficLayer);
            this.updateTrafficData();
        } else {
            this.map.layers.remove(this.trafficLayer);
            document.getElementById('free-roads').textContent = '0';
            document.getElementById('loaded-roads').textContent = '0';
            document.getElementById('traffic-jams').textContent = '0';
            document.getElementById('heavy-jams').textContent = '0';
            document.getElementById('jam-list').innerHTML = '<p class="text-muted">Слой пробок отключен</p>';
        }

        const button = document.getElementById('toggleTraffic');
        if (this.isTrafficVisible) {
            button.innerHTML = '<i class="bi bi-car-front me-1"></i>Скрыть пробки';
            button.classList.remove('btn-outline-secondary');
            button.classList.add('btn-outline-primary');
        } else {
            button.innerHTML = '<i class="bi bi-car-front-fill me-1"></i>Показать пробки';
            button.classList.remove('btn-outline-primary');
            button.classList.add('btn-outline-secondary');
        }
    }

    focusOnSmolensk() {
        if (this.map) {
            this.map.setCenter([54.7818, 32.0401], 13);
        }
    }

    showAllRegion() {
        if (this.map) {
            this.map.setBounds(this.smolenskBounds, {
                checkZoomRange: true,
                zoomMargin: 10
            });
        }
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    window.mapManager = new YandexMapManager();
});