const popup = () => {
    const pop_window = document.querySelector(".pop-up")

    if (!sessionStorage.getItem("popup")) {
        setTimeout(() => {
            pop_window.style.display = "block";
            sessionStorage.setItem("popup", true)
        }, 1000)
    }
}

const sidenav = () => {
    // For side nav
    var elems = document.querySelectorAll('.sidenav');
    var instances = M.Sidenav.init(elems, {});
}

const flash_messages = () => {
    setTimeout(() => {
        const messages = document.querySelector(".messages");
        if (messages) {
            messages.style.display = "None";
        }
    }, 3000)
}

const model_triggers = () => {
    document.querySelectorAll(".modal-trigger").forEach(trigger => {
        trigger.addEventListener("click", (event) => {
            event.preventDefault(); // Prevent default anchor behavior

            // Extract modal ID from href attribute (e.g., #edit-review)
            const modal_id = trigger.getAttribute("href").replace("#", "");

            // Pass the trigger element to the models function
            models(modal_id, trigger);
        });
    });
}

const initialize_select_dropdown = () => {
    const elems = document.querySelectorAll('select');
    M.FormSelect.init(elems);
};

// Created this function to handle all modals 
const models = (modal_id, trigger) => {
    // Get the modal element by ID
    const modalElem = document.getElementById(modal_id);

    if (modalElem) {
        // Initialize the modal
        const instance = M.Modal.init(modalElem, {});

        // Open the modal
        instance.open();

        // If the modal is the edit-review modal
        if (modal_id === "edit-review") {
            const review_id = trigger.getAttribute("data-id");
            const review_text = trigger.getAttribute("data-text")

            // Update form action dynamically
            const form = document.getElementById("edit-review-form");
            form.setAttribute("action", `/edit_review/${review_id}`);

            const textarea_value = document.getElementById("edit-review-text")
            textarea_value.value = review_text
        }

        if (modal_id == "edit-deal") {
            const deal_id = trigger.getAttribute("data-id");
            const deal_text = trigger.getAttribute("data-text")

            // Update form action dynamically
            const form = document.getElementById("edit-deal-form");
            form.setAttribute("action", `/edit_promo/${deal_id}`);

            const textarea_value = document.getElementById("edit-review-text")
            textarea_value.placeholder = deal_text
        }
    } else {
        console.error(`Modal with ID '${modal_id}' not found.`);
    }
};

const review_style = () => {
    const row = document.querySelectorAll(".review-container");

    row.forEach((row, index) => {
        if (index % 2 == 0) {
            row.style.backgroundColor = "lightgrey";
            row.style.padding = "10px";
            row.style.marginBottom = "20px";
            row.style.borderRadius = "10px";
        }

        if (index == -1) {
            row.style.marginBottom = "200px";
        }
    });
}

// Get the hidden input datefeild and dynamicly insert date
const form_auto_date = () => {
    const datefeild = document.getElementById("datefeild");
    const today = new Date();
    const day = String(today.getDate()).padStart(2, '0'); // Ensure two digits
    const month = String(today.getMonth() + 1).padStart(2, '0'); // Month is 0-indexed
    const year = today.getFullYear();
    const formattedDate = `${day}-${month}-${year}`; // Format: dd-MM-YYYY
    datefeild.value = formattedDate;
}

const create_deal_datepicker = () => {
    const datePicker = document.querySelector('.datepicker');

    M.Datepicker.init(datePicker, {
        format: "dd-mm-yyyy",
        showClearBtn: true,
        autoClose: true,
        firstDay: 1,
        container: document.body,
        onOpen: function () {
            datePicker.removeAttribute("placeholder"); // Remove "dd/mm/yyyy"
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    popup();
    sidenav();
    flash_messages();
    model_triggers();
    initialize_select_dropdown();
    review_style();
    form_auto_date();
    create_deal_datepicker();
})