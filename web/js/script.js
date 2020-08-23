
/*
* Trigger a file open dialog and read local file, then read and log the file contents
*/
"use strict";

// Get original image size {width, height} as promise
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

// Read file as DataURL promise
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

// Class for text box on svg image
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
        this.add_mask(box.mask)
    }

    add_mask(mask_url) {
        var mask = document.getElementById('text_mask');
        this.mask_image = document.createElementNS('http://www.w3.org/2000/svg', 'image');
        this.mask_image.setAttributeNS(null, 'href', mask_url);
        mask.appendChild(this.mask_image);
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


// Class for svg image with text boxes
class ImageFrame {
    constructor(){
        this.image_url = null;
        this.svg = document.getElementById('image_field');
        this.width = image_field.clientWidth;
        console.log(this.svg);
        this.boxes = []
    }

    async add_image(image_url) {
        this.clean();
        var size = await getImageSize(image_url);
        // compute svg image size
        this.naturalWidth = size.width;
        this.naturalHeight = size.height;
        this.aspect_ratio = this.naturalWidth / this.naturalHeight;
        console.log(this.aspect_ratio);
        this.height = this.width / this.aspect_ratio;
        this.scale_to_local = this.width / this.naturalWidth;
        this.svg.setAttributeNS(null, 'viewBox', "0 0 " + this.naturalWidth + " " + this.naturalHeight);

        // Add image element on svg
        this.image = document.createElementNS('http://www.w3.org/2000/svg', 'image');

        this.image.setAttributeNS(null, 'href', image_url);
        this.image.setAttributeNS(null, 'width', this.naturalWidth);
        this.svg.appendChild(this.image);
        this.add_mask();
    }

    add_box(box) {
        this.boxes.push(new Box(this.svg, box));
    }

    add_mask() {
        this.defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        this.mask = document.createElementNS('http://www.w3.org/2000/svg', 'mask');
        this.mask.setAttributeNS(null, 'id', 'text_mask');
        /*
        var mask_image = document.createElementNS('http://www.w3.org/2000/svg', "circle");
        mask_image.setAttributeNS(null, 'cx', this.naturalWidth / 2);
        mask_image.setAttributeNS(null, 'cy', this.naturalHeight / 2);
        mask_image.setAttributeNS(null, 'r', this.naturalHeight / 6);
        mask_image.setAttributeNS(null, 'fill', "white");
        this.mask.appendChild(mask_image);
        */

        /*
        var mask_image = document.createElementNS('http://www.w3.org/2000/svg', 'image');
        mask_image.setAttributeNS(null, 'href', mask_url);
        mask_image.setAttributeNS(null, 'width', this.naturalWidth);
        this.mask.appendChild(mask_image);
        */

        this.defs.appendChild(this.mask);
        this.svg.appendChild(this.defs);


        this.mask_box = document.createElementNS('http://www.w3.org/2000/svg', "rect");
        this.mask_box.setAttributeNS(null, 'x', 0);
        this.mask_box.setAttributeNS(null, 'y', 0);
        this.mask_box.setAttributeNS(null, 'width', this.naturalWidth);
        this.mask_box.setAttributeNS(null, 'height', this.naturalHeight);
        this.mask_box.setAttributeNS(null, 'style', "fill:red;stroke-width:0;fill-opacity:1");
        this.mask_box.setAttributeNS(null, 'mask', 'url(#text_mask)');
        this.svg.appendChild(this.mask_box);

        /*
        var mask_box = document.createElementNS('http://www.w3.org/2000/svg', 'image');
        mask_box.setAttributeNS(null, 'href', mask_url);
        mask_box.setAttributeNS(null, 'width', this.naturalWidth);
        mask_box.setAttributeNS(null, 'mask', 'url(#text_mask)');
        this.svg.appendChild(mask_box);
        */
    }

    clean() {
        $("#image_field").empty();
    }
}

async function processImage() {
    let result = null;
    try {

        var dataURL = await readAsDataURL(fileInput.files[0]);
        //var server_url = 'http://192.168.1.64:8080';
        var server_url = "https://us-central1-comic-translate-284120.cloudfunctions.net/detect_text";

        let result = await $.ajax({
            url: server_url,
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

// Load new Image
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
