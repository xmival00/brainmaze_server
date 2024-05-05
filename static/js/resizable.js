document.addEventListener('DOMContentLoaded', function () {
    // Horizontal resizer
    const resizerHorizontal = document.getElementById('drag-resizer-horizontal');
    const topPanel = document.querySelector('.main-panel-top');
    const bottomPanel = document.querySelector('.main-panel-bottom');
    let startY, startTopHeight, startBottomHeight;

    resizerHorizontal.addEventListener('mousedown', function (e) {
        startY = e.clientY;
        startTopHeight = parseInt(document.defaultView.getComputedStyle(topPanel).height, 10);
        startBottomHeight = parseInt(document.defaultView.getComputedStyle(bottomPanel).height, 10);
        document.addEventListener('mousemove', horizontalMoveHandler);
        document.addEventListener('mouseup', stopResize);
    });

    function horizontalMoveHandler(e) {
        const diffY = e.clientY - startY;
        const newTopHeight = startTopHeight + diffY;
        const newBottomHeight = startBottomHeight - diffY;

        if (newTopHeight > 0 && newBottomHeight > 0) {
            topPanel.style.height = `${newTopHeight}px`;
            bottomPanel.style.height = `${newBottomHeight}px`;
        }
    }

    // Vertical resizer
    const resizerVertical = document.getElementById('drag-resizer-vertical');
    const leftPanel = document.querySelector('.main-panel-left');
    const rightPanel = document.querySelector('.main-panel-right');
    let startX, startLeftWidth, startRightWidth;

    resizerVertical.addEventListener('mousedown', function (e) {
        startX = e.clientX;
        startLeftWidth = parseInt(document.defaultView.getComputedStyle(leftPanel).width, 10);
        startRightWidth = parseInt(document.defaultView.getComputedStyle(rightPanel).width, 10);
        document.addEventListener('mousemove', verticalMoveHandler);
        document.addEventListener('mouseup', stopResize);
    });

    function verticalMoveHandler(e) {
        const diffX = e.clientX - startX;
        const newLeftWidth = startLeftWidth + diffX;
        const newRightWidth = startRightWidth - diffX;

        if (newLeftWidth > 0 && newRightWidth > 0) {
            leftPanel.style.width = `${newLeftWidth}px`;
            rightPanel.style.width = `${newRightWidth}px`;
        }
    }

    function stopResize() {
        document.removeEventListener('mousemove', horizontalMoveHandler);
        document.removeEventListener('mousemove', verticalMoveHandler);
        document.removeEventListener('mouseup', stopResize);
    }
});
