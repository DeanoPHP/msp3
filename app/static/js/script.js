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

document.addEventListener("DOMContentLoaded", () => {
    sidenav();
    flash_messages();
})