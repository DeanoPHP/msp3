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
            console.log(review_text)
            textarea_value.placeholder = review_text
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

document.addEventListener("DOMContentLoaded", () => {
    sidenav();
    flash_messages();
    model_triggers();
    review_style();
})