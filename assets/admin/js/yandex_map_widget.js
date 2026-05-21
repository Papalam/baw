(function () {
    const YANDEX_API_KEY = '05aad1ac-b2d0-4a4b-a44d-96081ed9d811';

    function initYandexMapWidgets() {
        document.querySelectorAll('.yandex-map-container').forEach(function (container) {
            const latInput      = container.querySelector('.ymap-lat');
            const lonInput      = container.querySelector('.ymap-lon');
            const mapDiv        = container.querySelector('.ymap-canvas');
            const searchInput   = container.querySelector('.ymap-search');
            const searchBtn     = container.querySelector('.ymap-search-btn');
            const clearBtn      = container.querySelector('.ymap-clear-btn');
            const coordsDisplay = container.querySelector('.ymap-coords-display');

            if (!mapDiv) return;

            const initialLat = parseFloat(latInput.value);
            const initialLon = parseFloat(lonInput.value);
            const center = (initialLat && initialLon)
                ? [initialLat, initialLon]
                : [55.751244, 37.618423];

            const map = new ymaps.Map(mapDiv, {
                center: center,
                zoom: (initialLat && initialLon) ? 15 : 10,
                controls: ['zoomControl', 'fullscreenControl']
            });

            setTimeout(function () {
                map.container.fitToViewport();
            }, 300);

            let placemark = null;

            function setPlacemark(coords, address) {
                if (placemark) map.geoObjects.remove(placemark);
                placemark = new ymaps.Placemark(coords, {
                    balloonContent: address || 'Выбранная точка'
                }, {
                    draggable: true,
                    preset: 'islands#redDotIcon'
                });
                placemark.events.add('dragend', function () {
                    const c = placemark.geometry.getCoordinates();
                    updateCoords(c);
                    reverseGeocode(c);
                });
                map.geoObjects.add(placemark);
            }

            function updateCoords(coords) {
                const lat = coords[0].toFixed(6);
                const lon = coords[1].toFixed(6);
                latInput.value = lat;
                lonInput.value = lon;
                coordsDisplay.textContent = `Широта: ${lat}, Долгота: ${lon}`;
            }

            function reverseGeocode(coords) {
                ymaps.geocode(coords).then(function (res) {
                    const obj = res.geoObjects.get(0);
                    if (obj && placemark) {
                        placemark.properties.set('balloonContent', obj.getAddressLine());
                    }
                });
            }

            function searchAddress() {
                const query = searchInput.value.trim();
                if (!query) return;
                ymaps.geocode(query, {results: 1}).then(function (res) {
                    const obj = res.geoObjects.get(0);
                    if (obj) {
                        const coords = obj.geometry.getCoordinates();
                        map.setCenter(coords, 15);
                        updateCoords(coords);
                        setPlacemark(coords, obj.getAddressLine());
                    } else {
                        alert('Адрес не найден');
                    }
                });
            }

            map.events.add('click', function (e) {
                const coords = e.get('coords');
                updateCoords(coords);
                reverseGeocode(coords);
                setPlacemark(coords);
            });

            if (initialLat && initialLon) {
                setPlacemark([initialLat, initialLon]);
                reverseGeocode([initialLat, initialLon]);
            }

            searchBtn.addEventListener('click', searchAddress);
            searchInput.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') { e.preventDefault(); searchAddress(); }
            });
            clearBtn.addEventListener('click', function () {
                latInput.value = '';
                lonInput.value = '';
                coordsDisplay.textContent = 'Координаты не заданы';
                if (placemark) { map.geoObjects.remove(placemark); placemark = null; }
                searchInput.value = '';
            });
        });
    }

    function loadYandexMaps() {
        if (typeof ymaps !== 'undefined') {
            ymaps.ready(initYandexMapWidgets);
            return;
        }
        const script = document.createElement('script');
        script.src = `https://api-maps.yandex.ru/2.1/?apikey=${YANDEX_API_KEY}&lang=ru_RU`;
        script.onload = function () { ymaps.ready(initYandexMapWidgets); };
        document.head.appendChild(script);
    }

    loadYandexMaps();

})();
