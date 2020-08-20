
/*
* Trigger a file open dialog and read local file, then read and log the file contents
*/
"use strict";

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

function createObjectURL(object) {
    return (window.URL) ? window.URL.createObjectURL(object) : window.webkitURL.createObjectURL(object);
}

function revokeObjectURL(url) {
    return (window.URL) ? window.URL.revokeObjectURL(url) : window.webkitURL.revokeObjectURL(url);
}

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
        this.scale_to_local = this.width / this.naturalWidth;
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
        var scaled_box = {
            'left': box.left * this.scale_to_local,
            'top': box.top * this.scale_to_local,
            'width': box.width * this.scale_to_local,
            'height': box.height * this.scale_to_local
        };
        this.boxes.push(new Box(this.svg, scaled_box));
    }

    clean() {
        this.svg.removeChild(this.image);
        for (box of this.boxes) {
            box.clean();
        }
    }
}

async function processImage() {
    var xhttp = new XMLHttpRequest();
    let result;
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText)
        }
    };
    try {

        var dataURL = await readAsDataURL(fileInput.files[0]);

        let result = await $.ajax({
            url: "https://us-central1-comic-translate-284120.cloudfunctions.net/detect_text",
            type: 'POST',
            async: true,
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({'image_url': dataURL})
        });

        Object.entries(result).forEach(([k,v]) => {
            imageFrame.add_box(v);
        });

        console.log(result);
    } catch (e) {
        console.warn(e.message)
    }
}


var fileInput = document.getElementById("file_input");
var imageFrame = null;

fileInput.click();

$('#file_input').on('change', function() {
    var file = fileInput.files[0];

    if (file.name.match(/\.(png|jpg|jpeg)$/)) {

        if(this.files.length) {
            var src = createObjectURL(file);

            imageFrame = new ImageFrame();
            imageFrame.add_image(src)
        }
    } else {
        alert("File not supported, .png or .jpg files only");
    }
});
