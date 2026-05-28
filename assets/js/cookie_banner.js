(function () {
    'use strict';

    var STORAGE_KEY = 'cookieConsent';
    var CONSENT_VER = 1;
    var EXPIRY_DAYS = 365;

    document.addEventListener('DOMContentLoaded', function () {
        var existing = loadConsent();
        if (existing && existing.version === CONSENT_VER) {
            applyConsent();
            return;
        }
        renderBanner();
    });

    function renderBanner() {
        var html =
            '<div class="cookie-banner" id="cookieBanner" role="dialog" aria-modal="true" aria-label="Согласие на использование cookie">' +
                '<div class="cookie-banner__inner">' +
                    '<p class="cookie-banner__title">Мы используем cookie</p>' +
                    '<p class="cookie-banner__text">' +
                        'Этот сайт использует файлы cookie для улучшения работы.' +
                    '</p>' +
                    '<div class="cookie-banner__btns">' +
                        '<button class="cookie-banner__btn cookie-banner__btn--accept" id="cookieBtnAccept">Принять</button>' +
                    '</div>' +
                '</div>' +
            '</div>';

        document.body.insertAdjacentHTML('beforeend', html);

        document.getElementById('cookieBtnAccept').addEventListener('click', function () {
            var data = {
                version: CONSENT_VER,
                savedAt: new Date().toISOString()
            };
            saveConsent(data);
            applyConsent();
            closeBanner();
            document.dispatchEvent(new CustomEvent('cookieConsentSaved', { detail: data }));
        });
    }

    function closeBanner() {
        var banner = document.getElementById('cookieBanner');
        if (!banner) return;
        banner.classList.add('_hidden');
        setTimeout(function () {
            if (banner.parentNode) banner.parentNode.removeChild(banner);
        }, 400);
    }

    function applyConsent() {
        if (typeof window.onCookieConsent === 'function') {
            window.onCookieConsent();
        }
    }

    function saveConsent(data) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        } catch (e) {
            setCookie(STORAGE_KEY, JSON.stringify(data), EXPIRY_DAYS);
        }
    }

    function loadConsent() {
        try {
            var raw = localStorage.getItem(STORAGE_KEY);
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            var c = getCookie(STORAGE_KEY);
            return c ? JSON.parse(c) : null;
        }
    }

    function setCookie(name, value, days) {
        var expires = '';
        if (days) {
            var d = new Date();
            d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
            expires = '; expires=' + d.toUTCString();
        }
        document.cookie = name + '=' + encodeURIComponent(value) + expires + '; path=/; SameSite=Lax';
    }

    function getCookie(name) {
        var nameEQ = name + '=';
        var parts = document.cookie.split(';');
        for (var i = 0; i < parts.length; i++) {
            var part = parts[i].trim();
            if (part.indexOf(nameEQ) === 0) {
                return decodeURIComponent(part.substring(nameEQ.length));
            }
        }
        return null;
    }

    window.CookieConsent = {
        isAccepted: function () {
            var d = loadConsent();
            return !!(d && d.version === CONSENT_VER);
        },
        reset: function () {
            try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
            setCookie(STORAGE_KEY, '', -1);
            location.reload();
        }
    };

})();
