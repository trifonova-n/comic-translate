
/*
* Trigger a file open dialog and read local file, then read and log the file contents
*/

function createObjectURL(object) {
    return (window.URL) ? window.URL.createObjectURL(object) : window.webkitURL.createObjectURL(object);
}

function revokeObjectURL(url) {
    return (window.URL) ? window.URL.revokeObjectURL(url) : window.webkitURL.revokeObjectURL(url);
}

function processImage() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        console.log(this.responseText)
    }
  };
  xhttp.open("POST", "https://us-central1-comic-translate-284120.cloudfunctions.net/detect_text", true);

  xhttp.setRequestHeader("Content-type", "application/json");
  readImage(fileInput.files[0], xhttp);
}

function readImage(file, xhttp) {
    // Check if the file is an image.
    if (file.type && file.type.indexOf('image') === -1) {
        console.log('File is not an image.', file.type, file);
        return;
    }

    const reader = new FileReader();
    reader.addEventListener('load', (event) => {
        console.log('File was read');
        xhttp.send(JSON.stringify({'image_url': event.target.result}));
    });
    reader.readAsDataURL(file);
}

var fileInput = document.getElementById("file_input");

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

            var image_field = document.getElementById("image_field");

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
