(function () {
    'use strict';

    var dealersData = JSON.parse(document.getElementById('dealers-data').textContent);

    ymaps.ready(function () {
        var myMap = new ymaps.Map('map', {
            center: [55.76, 37.64],
            zoom: 10
        });

        var placemarks = dealersData.map(function (dealer) {
            var placemark = new ymaps.Placemark([dealer.lat, dealer.lng], {
                balloonContentHeader: dealer.name,
                balloonContentBody: dealer.address + '<br>' + dealer.phone
            });
            myMap.geoObjects.add(placemark);
            return placemark;
        });

        if (placemarks.length > 0) {
            myMap.setBounds(myMap.geoObjects.getBounds(), {
                checkZoomRange: true,
                zoomMargin: 50
            });
        }

        function showAllMarkers() {
            myMap.geoObjects.removeAll();
            placemarks.forEach(function (p) { myMap.geoObjects.add(p); });
            if (placemarks.length > 0) {
                myMap.setBounds(myMap.geoObjects.getBounds(), {
                    checkZoomRange: true,
                    zoomMargin: 50
                });
            }
        }

        $(document).on('click', '.dealer-item__show', function () {
            var pk = parseInt($(this).closest('.dealer-item').data('dealer-pk'));
            var idx = -1;
            dealersData.forEach(function (d, i) {
                if (d.pk === pk) idx = i;
            });
            if (idx === -1) return;

            myMap.geoObjects.removeAll();
            myMap.geoObjects.add(placemarks[idx]);
            myMap.setCenter([dealersData[idx].lat, dealersData[idx].lng], 14);
        });

        $(document).on('click', '.dealer-item__back', function () {
            showAllMarkers();
        });

        window.DealerMap = {
            selectByPk: function (pk) {
                var idx = -1;
                dealersData.forEach(function (d, i) {
                    if (d.pk === pk) idx = i;
                });
                if (idx === -1) return;

                myMap.geoObjects.removeAll();
                myMap.geoObjects.add(placemarks[idx]);
                myMap.setCenter([dealersData[idx].lat, dealersData[idx].lng], 14);
            }
        };
    });
})();
