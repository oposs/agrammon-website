(function () {
    'use strict';

    var STORAGE_KEY = 'ag-theme';
    var HTML = document.documentElement;

    function getEffectiveTheme() {
        return HTML.classList.contains('dark') ? 'dark' : 'light';
    }

    function applyTheme(theme) {
        if (theme === 'dark') {
            HTML.classList.add('dark');
        } else {
            HTML.classList.remove('dark');
        }
        // Update aria-labels
        var isDark = (theme === 'dark');
        var label = isDark ? 'Switch to light mode' : 'Switch to dark mode';
        ['ag-theme-toggle', 'ag-theme-toggle-mobile'].forEach(function (id) {
            var btn = document.getElementById(id);
            if (btn) {
                btn.setAttribute('aria-label', label);
                btn.setAttribute('title', label);
            }
        });
    }

    function handleToggle() {
        var next = getEffectiveTheme() === 'dark' ? 'light' : 'dark';
        localStorage.setItem(STORAGE_KEY, next);
        applyTheme(next);
    }

    document.addEventListener('DOMContentLoaded', function () {
        ['ag-theme-toggle', 'ag-theme-toggle-mobile'].forEach(function (id) {
            var btn = document.getElementById(id);
            if (btn) btn.addEventListener('click', handleToggle);
        });

        // Sync with OS preference changes when no stored preference
        var mq = window.matchMedia('(prefers-color-scheme: dark)');
        var handler = function (e) {
            if (localStorage.getItem(STORAGE_KEY)) return;
            applyTheme(e.matches ? 'dark' : 'light');
        };
        if (mq.addEventListener) {
            mq.addEventListener('change', handler);
        } else {
            mq.addListener(handler);
        }
    });
}());
