
/*
* Trigger a file open dialog and read local file, then read and log the file contents
*/

function createObjectURL(object) {
    return (window.URL) ? window.URL.createObjectURL(object) : window.webkitURL.createObjectURL(object);
}

function revokeObjectURL(url) {
    return (window.URL) ? window.URL.revokeObjectURL(url) : window.webkitURL.revokeObjectURL(url);
}

function myUploadOnChangeFunction() {
    if(this.files.length) {
        var src = createObjectURL(this.files[0]);
        var image = new Image();
        image.src = src;
        // Do whatever you want with your image, it's just like any other image
        // but it displays directly from the user machine, not the server!
    }
}

var fileInput = document.getElementById("file_input")

fileInput.addEventListener('change', function() {
    var file = fileInput.files[0];

    if (file.name.match(/\.(png|jpg|jpeg)$/)) {
        /*
        var reader = new FileReader();

        reader.onload = function() {
            console.log(reader.result);
        };

        reader.readAsText(file);
        */
        if(this.files.length) {
            var src = createObjectURL(this.files[0]);

            var image_field = document.getElementById("image_field")

            //var image = new Image();
            //image.src = src;
            image_field.innerHTML = "<img src=\"" + src + "\" style=\"width:600px;\"\>"
            // Do whatever you want with your image, it's just like any other image
            // but it displays directly from the user machine, not the server!
        }
    } else {
        alert("File not supported, .png or .jpg files only");
    }
});

fileInput.click();
