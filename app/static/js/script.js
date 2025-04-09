/* jshint esversion: 6 */
/* global M, sessionStorage */

// Show the popup on first visit, using sessionStorage to avoid repeat
const popup = () => {
    const pop_window = document.querySelector(".pop-up");

    if (!sessionStorage.getItem("popup")) {
        setTimeout(() => {
            pop_window.style.display = "block";
            sessionStorage.setItem("popup", true);
        }, 1000);
    }
};

// Initialize Materialize side navigation component
const sidenav = () => {
    var elems = document.querySelectorAll('.sidenav');
    M.Sidenav.init(elems, {});
};

// Automatically hide flash messages after 3 seconds
const flash_messages = () => {
    setTimeout(() => {
        const messages = document.querySelector(".messages");
        if (messages) {
            messages.style.display = "None";
        }
    }, 3000);
};

// Attach click listeners to all modal triggers to open corresponding modals
const model_triggers = () => {
    document.querySelectorAll(".modal-trigger").forEach((trigger) => {
        trigger.addEventListener("click", (event) => {
            event.preventDefault();
            const modal_id = trigger.getAttribute("href").replace("#", "");
            models(modal_id, trigger);
        });
    });
};

// Initialize Materialize <select> dropdown elements
const initialize_select_dropdown = () => {
    const elems = document.querySelectorAll('select');
    M.FormSelect.init(elems);
};

// Handle and open different modals based on their ID
const models = (modal_id, trigger) => {
    const modalElem = document.getElementById(modal_id);

    if (modalElem) {
        const instance = M.Modal.init(modalElem, {});
        instance.open();

        // Fill edit-review modal fields dynamically
        if (modal_id === "edit-review") {
            const review_id = trigger.getAttribute("data-id");
            const review_text = trigger.getAttribute("data-text");
            const form = document.getElementById("edit-review-form");
            form.setAttribute("action", `/edit_review/${review_id}`);
            const textarea_value = document.getElementById("edit-review-text");
            textarea_value.value = review_text;
        }

        // Fill edit-deal modal fields dynamically
        if (modal_id === "edit-deal") {
            const deal_id = trigger.getAttribute("data-id");
            const deal_text = trigger.getAttribute("data-text");
            const form = document.getElementById("edit-deal-form");
            form.setAttribute("action", `/edit_promo/${deal_id}`);
            const textarea_value = document.getElementById("edit-review-text");
            textarea_value.placeholder = deal_text;
        }
    } else {
        console.error(`Modal with ID '${modal_id}' not found.`);
    }
};

// Add alternating background styles to review containers
const review_style = () => {
    const row = document.querySelectorAll(".review-container");

    row.forEach((row, index) => {
        if (index % 2 === 0) {
            row.style.backgroundColor = "lightgrey";
            row.style.padding = "10px";
            row.style.marginBottom = "20px";
            row.style.borderRadius = "10px";
        }

        if (index === -1) {
            row.style.marginBottom = "200px";
        }
    });
};

// Automatically fill hidden date input with today's date in dd-mm-yyyy format
const form_auto_date = () => {
    const datefeild = document.getElementById("datefeild");
    const today = new Date();
    const day = String(today.getDate()).padStart(2, '0');
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const year = today.getFullYear();
    const formattedDate = `${day}-${month}-${year}`;
    datefeild.value = formattedDate;
};

// Initialize Materialize date picker for promo/expiry dates
const create_deal_datepicker = () => {
    const datePicker = document.querySelector('.datepicker');

    M.Datepicker.init(datePicker, {
        format: "dd-mm-yyyy",
        showClearBtn: true,
        autoClose: true,
        firstDay: 1,
        container: document.body,
        onOpen: function () {
            datePicker.removeAttribute("placeholder");
        }
    });
};

// Run all functions after DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    popup();
    sidenav();
    flash_messages();
    model_triggers();
    initialize_select_dropdown();
    review_style();
    form_auto_date();
    create_deal_datepicker();
});
