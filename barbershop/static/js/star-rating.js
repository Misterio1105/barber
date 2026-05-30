(function () {
    function setRating(picker, value) {
        var input = picker.querySelector('input[type="hidden"]');
        if (!input) return;

        input.value = value;

        picker.querySelectorAll(".star-pick").forEach(function (star) {
            var starValue = parseInt(star.dataset.value, 10);
            var isLit = starValue <= value;
            star.textContent = isLit ? "★" : "☆";
            star.classList.toggle("is-active", isLit);
        });
    }

    document.querySelectorAll(".star-rating-picker").forEach(function (picker) {
        var input = picker.querySelector('input[type="hidden"]');
        var stars = picker.querySelectorAll(".star-pick");
        if (!input || !stars.length) return;

        stars.forEach(function (star) {
            star.addEventListener("click", function () {
                setRating(picker, parseInt(star.dataset.value, 10));
            });
        });

        setRating(picker, parseInt(input.value, 10) || 5);
    });
})();
