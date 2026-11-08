/**
 * Лабораторная работа №7 (ПСИП) — Визуальные эффекты и анимация на HTML-странице
 * Скрипт интерактивного управления слайдером и вспомогательными эффектами
 * Студент: Лабынцев Денис Янушевич • Группа: РС02-23
 */

document.addEventListener("DOMContentLoaded", () => {
    // --------------------------------------------------------------------------
    // 1. Управление слайдером изображений (Задание 5)
    // --------------------------------------------------------------------------
    const sliderTrack = document.getElementById("sliderTrack");
    const slides = document.querySelectorAll(".slide");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const dots = document.querySelectorAll(".dot");

    let currentSlide = 0;
    const totalSlides = slides.length;
    let autoSlideInterval = null;

    function updateSlider(index) {
        currentSlide = (index + totalSlides) % totalSlides;
        const offset = -currentSlide * 100;
        if (sliderTrack) {
            sliderTrack.style.transform = `translateX(${offset}%)`;
        }

        // Обновление активной точки пагинации
        dots.forEach((dot, idx) => {
            if (idx === currentSlide) {
                dot.classList.add("active");
            } else {
                dot.classList.remove("active");
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", () => {
            updateSlider(currentSlide + 1);
            resetAutoplay();
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener("click", () => {
            updateSlider(currentSlide - 1);
            resetAutoplay();
        });
    }

    dots.forEach((dot) => {
        dot.addEventListener("click", (e) => {
            const index = parseInt(e.target.getAttribute("data-index"), 10);
            updateSlider(index);
            resetAutoplay();
        });
    });

    // Автоматическая смена слайдов каждые 4.5 секунды
    function startAutoplay() {
        autoSlideInterval = setInterval(() => {
            updateSlider(currentSlide + 1);
        }, 4500);
    }

    function resetAutoplay() {
        if (autoSlideInterval) {
            clearInterval(autoSlideInterval);
            startAutoplay();
        }
    }

    // Приостановка автопрокрутки при наведении курсора на слайдер
    const sliderContainer = document.querySelector(".slider-container");
    if (sliderContainer) {
        sliderContainer.addEventListener("mouseenter", () => {
            if (autoSlideInterval) clearInterval(autoSlideInterval);
        });
        sliderContainer.addEventListener("mouseleave", () => {
            startAutoplay();
        });
    }

    startAutoplay();

    // --------------------------------------------------------------------------
    // 2. Интерактивная подсветка активного пункта навигации при скролле (Задание 3)
    // --------------------------------------------------------------------------
    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll(".nav-link");

    window.addEventListener("scroll", () => {
        let scrollY = window.pageYOffset;

        sections.forEach((sec) => {
            const sectionHeight = sec.offsetHeight;
            const sectionTop = sec.offsetTop - 120;
            const sectionId = sec.getAttribute("id");

            if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                navLinks.forEach((link) => {
                    link.classList.remove("active");
                    if (link.getAttribute("href") === `#${sectionId}`) {
                        link.classList.add("active");
                    }
                });
            }
        });
    });

    // --------------------------------------------------------------------------
    // 3. Микро-параллакс для карточки талисмана (Задание 1 и 2)
    // --------------------------------------------------------------------------
    const mascotCard = document.querySelector(".floating-mascot-card");
    if (mascotCard) {
        document.addEventListener("mousemove", (e) => {
            const { clientX, clientY } = e;
            const xOffset = (clientX / window.innerWidth - 0.5) * 15;
            const yOffset = (clientY / window.innerHeight - 0.5) * 15;
            mascotCard.style.transform = `translateY(${yOffset - 5}px) rotate(${xOffset * 0.2}deg)`;
        });
    }
});
