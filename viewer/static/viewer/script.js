document.addEventListener("DOMContentLoaded", function() {
    // Přepínání obrázků v detailu hry
    function initializeGameCardImages() {
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
        }
    }

    // Animace karet
    function initializeCardAnimations() {
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
                }, index * 100); // Zpoždění pro každou kartu
            });
        }, 100);
    }

    // Přepínání obrázků a videí v detailu hry
    function initializeMediaThumbnails() {
        const thumbnails = document.querySelectorAll(".thumbnail");
        if (thumbnails.length > 0) {
            thumbnails.forEach(thumbnail => {
                thumbnail.addEventListener("click", function() {
                    const mainMediaContainer = document.querySelector('.main-media');
                    const isVideo = thumbnail.dataset.isVideo === 'true';
                    const mediaUrl = thumbnail.dataset.url;

                    showMainMedia(mediaUrl, isVideo);
                });
            });
        }
    }

    // Zobrazení hlavního média (obrázek nebo video)
    function showMainMedia(url, isVideo = false) {
        const mainMediaContainer = document.querySelector('.main-media');

        if (isVideo) {
            mainMediaContainer.innerHTML = `<iframe width="100%" height="460" src="https://www.youtube.com/embed/${url.split('v=')[1]}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
        } else {
            mainMediaContainer.innerHTML = `<img src="${url}" alt="Hlavní obrázek" class="detail-image">`;
        }
    }

    // Šipky pro přepínání mezi obrázky/videi
    function initializeMediaArrows() {
        const prevArrow = document.querySelector("#prev-arrow");
        const nextArrow = document.querySelector("#next-arrow");
        let currentMediaIndex = 0;

        function updateMainMedia(index) {
            const mediaThumbnails = document.querySelectorAll(".thumbnail");
            const isVideo = mediaThumbnails[index].dataset.isVideo === 'true';
            const mediaUrl = mediaThumbnails[index].dataset.url;

            showMainMedia(mediaUrl, isVideo);
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

        if (prevArrow && nextArrow) {
            prevArrow.addEventListener("click", showPrevMedia);
            nextArrow.addEventListener("click", showNextMedia);
        }
    }

    // Wishlist
    function initializeWishlist() {
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
    }

    // Funkce pro aktualizaci položek v košíku
    function initializeCartQuantityButtons() {
        const quantityButtons = document.querySelectorAll('.quantity-btn');
        quantityButtons.forEach(button => {
            button.addEventListener('click', function() {
                const action = this.dataset.action;
                const itemId = this.dataset.itemId;
                const quantityElement = this.closest('.quantity-controls').querySelector('.quantity-number');
                let currentQuantity = parseInt(quantityElement.textContent);

                if (action === 'increase') {
                    currentQuantity++;
                } else if (action === 'decrease') {
                    currentQuantity--;
                }

                if (currentQuantity <= 0) {
                    fetch(`/remove-from-cart/${itemId}/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            this.closest('li').remove();
                            if (document.getElementById('total-price')) {
                                document.getElementById('total-price').textContent = data.new_total_price;
                            }
                        } else {
                            console.error('Failed to remove the cart item.');
                        }
                    })
                    .catch(error => {
                        console.error('Error removing cart item:', error);
                    });
                } else {
                    quantityElement.textContent = currentQuantity;

                    fetch(`/update-cart-item/${itemId}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        },
                        body: JSON.stringify({
                            'quantity': currentQuantity
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            const priceElement = this.closest('.cart-item-info').querySelector('.price, .discounted-price');
                            if (priceElement) {
                                priceElement.textContent = data.new_price + ' Kč';
                            }

                            if (document.getElementById('total-price')) {
                                document.getElementById('total-price').textContent = data.new_total_price;
                            }
                        } else {
                            console.error('Failed to update the cart item.');
                        }
                    })
                    .catch(error => {
                        console.error('Error updating cart item:', error);
                    });
                }
            });
        });
    }

    function dismissAddAnotherPopup(window, newId, newName) {
        const genresSelect = document.getElementById("id_genres"); // Najdeme výběrové pole
        if (genresSelect) {
            const newOption = new Option(newName, newId); // Vytvoříme novou možnost
            genresSelect.add(newOption, undefined); // Přidáme ji do seznamu
            genresSelect.value = newId; // Nastavíme nově přidaný žánr jako vybraný
        }
        window.close(); // Zavřeme popup
    }

    // Inicializace funkcí po načtení stránky
    initializeGameCardImages();
    initializeCardAnimations();
    initializeMediaThumbnails();
    initializeMediaArrows();
    initializeWishlist();
    initializeCartQuantityButtons();
});
