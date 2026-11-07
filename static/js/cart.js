(function () {
    const table = document.getElementById("cart-table");
    if (!table) {
        return;
    }

    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    const totalCell = document.querySelector("[data-cart-total]");
    const countCell = document.querySelector("[data-cart-count]");
    const headerCount = document.getElementById("cart-count");
    const summaryLine = document.getElementById("cart-summary-line");

    function post(url, body) {
        return fetch(url, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: body,
        }).then(function (response) {
            if (!response.ok) {
                throw new Error("Request failed");
            }
            return response.json();
        });
    }

    function paint(data) {
        if (totalCell) {
            totalCell.textContent = "$" + data.cart_total;
        }
        if (countCell) {
            countCell.textContent = data.cart_count;
        }
        if (headerCount) {
            headerCount.textContent = data.cart_count;
            headerCount.style.display = data.cart_count ? "" : "none";
        }
        if (summaryLine) {
            const rows = table.querySelectorAll("[data-row]").length;
            summaryLine.textContent =
                rows + " product" + (rows === 1 ? "" : "s") + " in your cart";
        }
        if (!table.querySelectorAll("[data-row]").length) {
            window.location.reload();
        }
    }

    table.addEventListener("change", function (event) {
        const input = event.target.closest("[data-qty]");
        if (!input) {
            return;
        }

        const row = input.closest("[data-row]");
        const max = parseInt(input.max, 10);
        let quantity = parseInt(input.value, 10);

        if (isNaN(quantity) || quantity < 1) {
            quantity = 1;
        }
        if (quantity > max) {
            quantity = max;
        }
        input.value = quantity;

        input.disabled = true;
        post(input.dataset.url, "quantity=" + quantity)
            .then(function (data) {
                input.value = data.quantity;
                input.disabled = false;
                if (data.removed) {
                    row.remove();
                } else {
                    row.querySelector("[data-line-total]").textContent =
                        "$" + data.line_total;
                }
                paint(data);
            })
            .catch(function () {
                input.disabled = false;
                window.location.reload();
            });
    });

    table.addEventListener("submit", function (event) {
        const form = event.target.closest("[data-remove]");
        if (!form) {
            return;
        }
        event.preventDefault();

        const row = form.closest("[data-row]");
        post(form.action, "")
            .then(function (data) {
                row.remove();
                paint(data);
            })
            .catch(function () {
                window.location.reload();
            });
    });
})();
