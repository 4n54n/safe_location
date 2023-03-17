function getLocation() {

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(sendCoordinates);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}


function sendCoordinates(position) {
    var latitude = position.coords.latitude;
    var longitude = position.coords.longitude;

    fetch("http://127.0.0.1:5000/", {
        method: "POST",
        body: JSON.stringify({
            latitude: latitude,
            longitude: longitude
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8",
            'Access-Control-Allow-Origin': '*'
        }
    })
        .then((response) => response.json())
        .then((json) => {
            document.open()
            document.write(json['result'])
            document.close()
        })
}
