function confirmOperation(url) {
    var res = confirm("Are you sure?");
    if (res == true) {
        window.location = url;
    }
}
