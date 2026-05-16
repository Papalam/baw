/**
 * Cookie Banner
 * Зависимости: jQuery (уже подключён в проекте)
 * Сохраняет выбор в localStorage по ключу 'cookieConsent'
 *
 * Структура данных в localStorage:
 * {
 *   "version": 1,
 *   "savedAt": "ISO-дата",
 *   "categories": {
 *     "necessary": true,      // всегда true
 *     "analytics": true|false,
 *     "functional": true|false
 *   }
 * }
 */

(function () {
    'use strict';

    /* ---- Конфигурация ---- */
    var STORAGE_KEY   = 'cookieConsent';
    var CONSENT_VER   = 1;
    var EXPIRY_DAYS   = 365;

    /* ---- Инициализация ---- */
    document.addEventListener('DOMContentLoaded', function () {
        var existing = loadConsent();
        if (existing && existing.version === CONSENT_VER) {
            // Выбор уже сохранён — баннер не показываем, применяем настройки
            applyConsent(existing.categories);
            return;
        }
        renderBanner();
    });

    /* ================================================================
       Рендер баннера
    ================================================================ */
    function renderBanner() {
        var html = '' +
            '<div class="cookie-banner" id="cookieBanner" role="dialog" aria-modal="true" aria-label="Настройки cookie">' +
                '<div class="cookie-banner__inner">' +
                    '<p class="cookie-banner__title">Мы используем cookie</p>' +
                    '<p class="cookie-banner__text">' +
                        'Этот сайт использует файлы cookie для улучшения работы. ' +
                        'Нажмите «Принять все» или настройте параметры самостоятельно.' +
                    '</p>' +
                    '<div class="cookie-banner__btns">' +
                        '<button class="cookie-banner__btn cookie-banner__btn--accept" id="cookieBtnAccept">Принять все</button>' +
                        '<button class="cookie-banner__btn cookie-banner__btn--necessary" id="cookieBtnNecessary">Только необходимые</button>' +
                        '<button class="cookie-banner__btn cookie-banner__btn--settings" id="cookieBtnSettings">Настройки cookie</button>' +
                    '</div>' +
                '</div>' +

                '<div class="cookie-banner__settings" id="cookieSettings">' +
                    '<p class="cookie-banner__settings-title">Управление категориями</p>' +

                    buildCheckRow(
                        'necessary',
                        'Необходимые',
                        'Обеспечивают базовую работу сайта. Не могут быть отключены.',
                        true,
                        true
                    ) +
                    buildCheckRow(
                        'analytics',
                        'Аналитика',
                        'Помогают понимать, как посетители используют сайт (Яндекс.Метрика, GA).',
                        false,
                        false
                    ) +
                    buildCheckRow(
                        'functional',
                        'Функциональные',
                        'Запоминают ваши предпочтения: язык, город, настройки отображения.',
                        false,
                        false
                    ) +

                    '<button class="cookie-banner__btn--save" id="cookieBtnSave">Сохранить настройки</button>' +
                '</div>' +
            '</div>';

        document.body.insertAdjacentHTML('beforeend', html);
        bindEvents();
    }

    function buildCheckRow(id, name, desc, checked, disabled) {
        var checkedAttr  = checked  ? ' checked'  : '';
        var disabledAttr = disabled ? ' disabled' : '';
        return '' +
            '<div class="cookie-check">' +
                '<div class="cookie-check__info">' +
                    '<p class="cookie-check__name">' + name + (disabled ? ' <small style="opacity:.5;font-weight:400">(всегда вкл.)</small>' : '') + '</p>' +
                    '<p class="cookie-check__desc">' + desc + '</p>' +
                '</div>' +
                '<label class="cookie-toggle">' +
                    '<input type="checkbox" id="cookie_' + id + '" data-cookie-cat="' + id + '"' + checkedAttr + disabledAttr + '>' +
                    '<span class="cookie-toggle__track"><span class="cookie-toggle__thumb"></span></span>' +
                '</label>' +
            '</div>';
    }

    /* ================================================================
       Привязка событий
    ================================================================ */
    function bindEvents() {
        document.getElementById('cookieBtnAccept').addEventListener('click', function () {
            saveAndClose({ necessary: true, analytics: true, functional: true });
        });

        document.getElementById('cookieBtnNecessary').addEventListener('click', function () {
            saveAndClose({ necessary: true, analytics: false, functional: false });
        });

        document.getElementById('cookieBtnSettings').addEventListener('click', function () {
            var panel = document.getElementById('cookieSettings');
            var isOpen = panel.classList.toggle('_open');
            this.textContent = isOpen ? 'Скрыть настройки' : 'Настройки cookie';
        });

        document.getElementById('cookieBtnSave').addEventListener('click', function () {
            var cats = {
                necessary: true,
                analytics:  getToggleValue('analytics'),
                functional: getToggleValue('functional')
            };
            saveAndClose(cats);
        });
    }

    function getToggleValue(cat) {
        var el = document.getElementById('cookie_' + cat);
        return el ? el.checked : false;
    }

    /* ================================================================
       Сохранение / закрытие
    ================================================================ */
    function saveAndClose(categories) {
        var data = {
            version: CONSENT_VER,
            savedAt: new Date().toISOString(),
            categories: categories
        };
        saveConsent(data);
        applyConsent(categories);
        closeBanner();

        // Событие для GTM / внешней аналитики
        document.dispatchEvent(new CustomEvent('cookieConsentSaved', { detail: data }));
    }

    function closeBanner() {
        var banner = document.getElementById('cookieBanner');
        if (!banner) return;
        banner.classList.add('_hidden');
        setTimeout(function () {
            if (banner.parentNode) banner.parentNode.removeChild(banner);
        }, 400);
    }

    /* ================================================================
       Применение согласия (подключение/отключение скриптов)
    ================================================================ */
    function applyConsent(categories) {
        // --- Аналитика ---
        // Здесь можно инициализировать Яндекс.Метрику, Google Analytics и т.д.
        // Пример: if (categories.analytics) { initYandexMetrika(); }
        if (typeof window.onCookieAnalytics === 'function') {
            window.onCookieAnalytics(categories.analytics);
        }

        // --- Функциональные ---
        if (typeof window.onCookieFunctional === 'function') {
            window.onCookieFunctional(categories.functional);
        }

        // Добавляем классы на <body> для возможной реакции других скриптов
        document.body.classList.toggle('cookie-analytics',  !!categories.analytics);
        document.body.classList.toggle('cookie-functional', !!categories.functional);
    }

    /* ================================================================
       Хранилище — localStorage + запасной вариант через cookie
    ================================================================ */
    function saveConsent(data) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        } catch (e) {
            // Fallback: браузерные cookie
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

    /* ---- Вспомогательные функции для cookie (fallback) ---- */
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
        var parts  = document.cookie.split(';');
        for (var i = 0; i < parts.length; i++) {
            var part = parts[i].trim();
            if (part.indexOf(nameEQ) === 0) {
                return decodeURIComponent(part.substring(nameEQ.length));
            }
        }
        return null;
    }

    /* ================================================================
       Публичное API — для использования из других скриптов
       Например: CookieConsent.getCategories().analytics
    ================================================================ */
    window.CookieConsent = {
        getCategories: function () {
            var d = loadConsent();
            return d ? d.categories : null;
        },
        isAccepted: function (category) {
            var cats = window.CookieConsent.getCategories();
            return cats ? !!cats[category] : false;
        },
        reset: function () {
            try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
            setCookie(STORAGE_KEY, '', -1);
            location.reload();
        }
    };

})();
