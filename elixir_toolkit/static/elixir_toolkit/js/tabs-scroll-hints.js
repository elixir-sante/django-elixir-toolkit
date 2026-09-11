function updateTabsScrollHints() {
    document.querySelectorAll('.tabs-scroll-wrapper').forEach(wrapper => {
        const scroller = wrapper.querySelector('.tabs');
        const leftHint = wrapper.querySelector('.tabs-scroll-hint-left');
        const rightHint = wrapper.querySelector('.tabs-scroll-hint-right');
        if (!scroller) return;

        const maxScroll = scroller.scrollWidth - scroller.clientWidth;
        if (leftHint) {
            leftHint.classList.toggle('is-hidden', maxScroll <= 1 || scroller.scrollLeft <= 1);
        }
        if (rightHint) {
            rightHint.classList.toggle('is-hidden', maxScroll <= 1 || scroller.scrollLeft >= maxScroll - 1);
        }
    });
}

function loadTabsScrollHints() {
    document.querySelectorAll('.tabs-scroll-wrapper').forEach(wrapper => {
        if (wrapper.dataset.hintBound) return;
        wrapper.dataset.hintBound = "1";

        const scroller = wrapper.querySelector('.tabs');
        const leftHint = wrapper.querySelector('.tabs-scroll-hint-left');
        const rightHint = wrapper.querySelector('.tabs-scroll-hint-right');
        if (!scroller) return;

        scroller.addEventListener('scroll', updateTabsScrollHints, { passive: true });
        if (leftHint) {
            leftHint.addEventListener('click', () => {
                scroller.scrollBy({ left: -scroller.clientWidth * 0.7, behavior: 'smooth' });
            });
        }
        if (rightHint) {
            rightHint.addEventListener('click', () => {
                scroller.scrollBy({ left: scroller.clientWidth * 0.7, behavior: 'smooth' });
            });
        }
    });
    updateTabsScrollHints();
}

window.addEventListener('resize', updateTabsScrollHints);

document.addEventListener('DOMContentLoaded', loadTabsScrollHints);
