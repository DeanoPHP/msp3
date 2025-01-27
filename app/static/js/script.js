const sidenav = () => {
    // For side nav
    var elems = document.querySelectorAll('.sidenav');
    var instances = M.Sidenav.init(elems, {});
}

document.addEventListener("DOMContentLoaded", () => {
    sidenav();
})