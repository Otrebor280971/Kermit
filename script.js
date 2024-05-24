var cameraContainer = document.getElementById("camera_container");
var videoElement = document.createElement("img");
videoElement.id = "drone_video";
videoElement.src = "http://192.168.10.2:5000/video_feed";
videoElement.alt = "Drone video feed";

cameraContainer.appendChild(videoElement);


function emergency_stop() {
    alert("Emergency stop")
    fetch("http://192.168.10.2:5000/emergency_stop")
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert(JSON.stringify(data));
            toggleOnAirText(false);
        })
        .catch(error => console.error('Error:', error));
}

function start() {
    alert("Starting drone sequences")
    fetch("http://192.168.10.2:5000/start")
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert(JSON.stringify(data));
            toggleOnAirText(True);
            updateReport(data);
        })
        .catch(error => console.error("Error:", error));
}

function toggleOnAirText(onAir) {
    var onAirElement = document.getElementById("onair");
    if (onAir) {
        onAirElement.textContent = "ON AIR";
    } else {
        onAirElement.textContent = "ON LAND";
    }
}

function updateReport(data) {
    var reportContainer = document.getElementById("report_container");
    reportContainer.innerHTML = "";

    for (var shape in data) {
        var shapeCount = data[shape];
        var shapeElement = document.createElement("p");
        shapeElement.textContent = shape + ": " + shapeCount;
        reportContainer.appendChild(shapeElement);

        var lineBreak = document.createElement("br");
        reportContainer.appendChild(lineBreak);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    toggleOnAirText(false);
});