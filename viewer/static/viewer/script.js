document.addEventListener("DOMContentLoaded", function() {
    const gameCards = document.querySelectorAll(".game-card-inner");

    if (gameCards.length > 0) {
        gameCards.forEach(card => {
            const images = card.querySelectorAll(".game-image");
            let currentIndex = 0;

            if (images.length > 1) {
                setInterval(() => {
                    images[currentIndex].style.display = 'none';
                    currentIndex = (currentIndex + 1) % images.length;
                    images[currentIndex].style.display = 'block';
                }, 2000);
            }
        });

        const gameCardContainers = document.querySelectorAll(".game-card");
        gameCardContainers.forEach((card, index) => {
            card.style.opacity = 0;
            card.style.transform = `translateX(${index % 2 === 0 ? '-' : ''}100vw)`;
        });

        setTimeout(() => {
            gameCardContainers.forEach((card, index) => {
                setTimeout(() => {
                    card.style.transition = 'transform 1s ease, opacity 1s ease';
                    card.style.transform = 'translateX(0)';
                    card.style.opacity = 1;
                }, index * 100); // Delay each card's animation slightly
            });
        }, 100);
    }

    // toggle pic
    const thumbnails = document.querySelectorAll(".thumbnail");
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener("click", function() {
            const mainMediaContainer = document.querySelector('.main-media');
            const isVideo = thumbnail.dataset.isVideo === 'true';
            const mediaUrl = thumbnail.dataset.url;

            if (isVideo) {
                mainMediaContainer.innerHTML = `<iframe width="100%" height="460" src="https://www.youtube.com/embed/${mediaUrl.split('v=')[1]}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
            } else {
                mainMediaContainer.innerHTML = `<img src="${mediaUrl}" alt="Hlavní obrázek" class="detail-image">`;
            }
            document.querySelector("#prev-arrow").style.display = 'block';
            document.querySelector("#next-arrow").style.display = 'block';
        });
    });

    // arrows
    const prevArrow = document.querySelector("#prev-arrow");
    const nextArrow = document.querySelector("#next-arrow");
    let currentMediaIndex = 0;

    function updateMainMedia(index) {
        const mediaThumbnails = document.querySelectorAll(".thumbnail");
        const mainMediaContainer = document.querySelector('.main-media');
        const isVideo = mediaThumbnails[index].dataset.isVideo === 'true';
        const mediaUrl = mediaThumbnails[index].dataset.url;

        if (isVideo) {
            mainMediaContainer.innerHTML = `<iframe width="100%" height="460" src="https://www.youtube.com/embed/${mediaUrl.split('v=')[1]}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
        } else {
            mainMediaContainer.innerHTML = `<img src="${mediaUrl}" alt="Hlavní obrázek" class="detail-image">`;
        }
        prevArrow.style.display = 'block';
        nextArrow.style.display = 'block';
    }

    function showPrevMedia() {
        const mediaThumbnails = document.querySelectorAll(".thumbnail");
        currentMediaIndex = (currentMediaIndex - 1 + mediaThumbnails.length) % mediaThumbnails.length;
        updateMainMedia(currentMediaIndex);
    }

    function showNextMedia() {
        const mediaThumbnails = document.querySelectorAll(".thumbnail");
        currentMediaIndex = (currentMediaIndex + 1) % mediaThumbnails.length;
        updateMainMedia(currentMediaIndex);
    }

    prevArrow.addEventListener("click", showPrevMedia);
    nextArrow.addEventListener("click", showNextMedia);

    // wishlist
    const wishlistForm = document.getElementById("wishlist-form");
    if (wishlistForm) {
        wishlistForm.addEventListener("submit", function(event) {
            event.preventDefault();

            const formData = new FormData(wishlistForm);

            fetch(wishlistForm.action, {
                method: "POST",
                headers: {
                    "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
                },
                body: formData,
            }).then(response => {
                if (response.ok) {
                    const isWishlisted = wishlistForm.querySelector("i.fas") !== null;
                    const buttonHtml = isWishlisted
                        ? '<i class="far fa-heart empty"></i>'
                        : '<i class="fas fa-heart filled"></i>';

                    wishlistForm.querySelector(".wishlist-icon").innerHTML = buttonHtml;
                }
            }).catch(error => {
                console.error("Error updating wishlist:", error);
            });
        });
    }
});
