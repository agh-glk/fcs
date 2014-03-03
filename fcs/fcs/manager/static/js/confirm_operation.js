function confirmOperation(url, text) {
    var res = confirm(text+"\nAre you sure?");
    if (res == true) {
        window.location = url;
    }
}
