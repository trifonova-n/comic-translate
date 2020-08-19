
/*
* Trigger a file open dialog and read local file, then read and log the file contents
*/
"use strict";

class Box{
    constructor(svg, box) {
        this.svg = svg;
        this.box = document.createElementNS('http://www.w3.org/2000/svg', "rect");
        this.box.setAttributeNS(null, 'x', box.left);
        this.box.setAttributeNS(null, 'y', box.top);
        this.box.setAttributeNS(null, 'width', box.width);
        this.box.setAttributeNS(null, 'height', box.height);
        this.box.setAttributeNS(null, 'style', "stroke:yellow;stroke-width:2;fill-opacity:0");

        this.svg.appendChild(this.box);
    }

    move(x, y) {
        this.box.setAttributeNS(null, 'x', x);
        this.box.setAttributeNS(null, 'y', y);
    }

    resize(width, height) {
        this.box.setAttributeNS(null, 'width', width);
        this.box.setAttributeNS(null, 'height', height);
    }

    clean() {
        this.svg.removeChild(this.box);
    }
}

function getImageSize(url){
    var img = new Image();
    var promise = new Promise( (resolve, reject) => {
            img.addEventListener("load", function(event){
                if (event.type == 'load') {
                    resolve({'width': this.naturalWidth, 'height': this.naturalHeight });
                }
                else {
                    reject("Unuble to get the size of image " + url);
                }
            });
        }

    );
    img.src = url;
    return promise;
}

class ImageFrame {
    constructor(){
        this.image_url = null;

        this.width = 800;
        this.svg = document.getElementById('image_field');
        console.log(this.svg);
        this.boxes = []
    }

    async add_image(image_url) {
        var size = await getImageSize(image_url);
        // compute svg image size
        this.naturalWidth = size.width;
        this.naturalHeight = size.height;
        this.aspect_ratio = this.naturalWidth / this.naturalHeight;
        console.log(this.aspect_ratio);
        this.height = this.width / this.aspect_ratio;
        this.svg.setAttributeNS(null, 'viewBox', "0 0 " + this.width + " " + this.height);
        this.svg.setAttributeNS(null, 'width', this.width);
        this.svg.setAttributeNS(null, 'height', this.height);

        // Add image element on svg
        this.image = document.createElementNS('http://www.w3.org/2000/svg', 'image');

        this.image.setAttributeNS(null, 'href', image_url);
        this.image.setAttributeNS(null, 'width', this.width);

        this.svg.appendChild(this.image);

    }

    add_box(box) {
        this.boxes.push(new Box(this.svg, box));
    }

    clean() {
        this.svg.removeChild(this.image);
        for (box of this.boxes) {
            box.clean();
        }
    }
}

function createObjectURL(object) {
    return (window.URL) ? window.URL.createObjectURL(object) : window.webkitURL.createObjectURL(object);
}

function revokeObjectURL(url) {
    return (window.URL) ? window.URL.revokeObjectURL(url) : window.webkitURL.revokeObjectURL(url);
}

async function processImage() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        console.log(this.responseText)
    }
  };
  try {
      xhttp.open("POST", "https://us-central1-comic-translate-284120.cloudfunctions.net/detect_text", true);

      xhttp.setRequestHeader("Content-type", "application/json");
      var dataURL = await readAsDataURL(fileInput.files[0]);

      xhttp.send(JSON.stringify({'image_url': dataURL}));
  } catch (e) {
      console.warn(e.message)
  }
}

function readAsDataURL(inputFile){
  var temporaryFileReader = new FileReader();

  return new Promise((resolve, reject) => {
    temporaryFileReader.onerror = () => {
      temporaryFileReader.abort();
      reject(new DOMException("Problem parsing input file."));
    };

    temporaryFileReader.onload = () => {
      resolve(temporaryFileReader.result);
    };
    temporaryFileReader.readAsDataURL(inputFile);
  });
}

var fileInput = document.getElementById("file_input");
var imageFrame = null;

fileInput.click();

$('#file_input').on('change', function() {
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

            imageFrame = new ImageFrame();
            imageFrame.add_image(src)

            // Do whatever you want with your image, it's just like any other image
            // but it displays directly from the user machine, not the server!
        }
    } else {
        alert("File not supported, .png or .jpg files only");
    }
});
