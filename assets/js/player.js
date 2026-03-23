document.addEventListener('DOMContentLoaded', function () {
    let activePlyr = null;

    Fancybox.bind('[data-fancybox="videos"]', {
        Hash: false,

        on: {
            // v4 использует "done" вместо "reveal"
            done: function (fancybox, slide) {
                const video = slide.$content?.querySelector('video');
                if (!video) return;

                activePlyr = new Plyr(video, {
                    controls: ['play', 'progress', 'current-time', 'mute', 'volume', 'fullscreen'],
                    hideControls: true,
                    clickToPlay: true,
                });

                activePlyr.on('ready', () => activePlyr.play().catch(() => {}));
            },

            // v4 использует "closing" так же как v5
            closing: function () {
                if (activePlyr) {
                    activePlyr.stop();
                    activePlyr.destroy();
                    activePlyr = null;
                }
            },
        },
    });
});