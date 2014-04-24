function askForPackageSize(url) {
    var strSize = prompt("Please enter size of package in MB:", "1");
    if (strSize != null && strSize.length > 0) {
        if(!isNaN(strSize) && parseInt(strSize) == strSize) {
            window.location = url + strSize;
        }
        else {
            alert("Value must be integer!");
        }
    }
}
