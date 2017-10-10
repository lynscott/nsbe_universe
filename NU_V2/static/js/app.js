
class MarvelCharacter {
    constructor(data) {
        this.id = data.id;
        this.name = data.name;
        this.description = data.description|| "n/a";
        this.thumbnail = data.thumbnail;
    }
    setImage() {
        return this.thumbnail.path +"."+ this.thumbnail.extension;

    }
}

function initMap() {
geocoder = new google.maps.Geocoder();
distance = new google.maps.DistanceMatrixService();
}

function geo_error() {
  alert("Sorry, no position available.");
}


$.getJSON("http://localhost:5000/users/JSON")
        .done(function(data){
            console.log(data);
            return users=data.users;
        }).fail(function() {
            alert("Error getting user data")
        });


var viewModel = {
    userInput : ko.observable(''),
    characterName : ko.observable(''),
    characterDesc : ko.observable(''),
    characterImage : ko.observable(''),
    toggleSubmit : ko.observable(false),
    toggleAlert : ko.observable(false),
    togglePass : ko.observable(false),
    pass1 : ko.observable(''),
    pass2 : ko.observable(''),
    currentPoints : ko.observable(),
    userLat : ko.observable(''),
    userLng : ko.observable(''),
    eventLocation : ko.observable(''),
    checkPass : function() {
        if (this.pass1() != this.pass2()) {
            return this.togglePass(true);
        }else {
            return this.togglePass(false);
        }
    },
    getInfo : function() {

        var base_url = 'https://gateway.marvel.com:443/v1/public/characters?';
        var api = '&apikey=194e9e5d5fcffb43dadcb84dc251c2b4';
        var character = 'name='+this.userInput();
        var found = null;

        var url = base_url+character+api;
        //Request Marvel Character Info
        $.getJSON(url)
            .done(function(result) {
                var data = result.data.results[0];

                //Display chracter info
                userCharacter = new MarvelCharacter(data);
                viewModel.characterName(userCharacter.name);
                viewModel.characterDesc(userCharacter.description);
                viewModel.characterImage(userCharacter.thumbnail.path+"."
                                    +userCharacter.thumbnail.extension);

                //Check if character is taken
                for (var i = 0; i < users.length; i++) {
                    if( viewModel.characterName() == users[i].alias ) {
                       found = true;
                       break;
                   }
                }
                if( found == true){
                    viewModel.toggleAlert(true);
                    return viewModel.toggleSubmit(false);
                }else {
                    found = false;
                    viewModel.toggleAlert(false);
                    return viewModel.toggleSubmit(true);
                }


            }).fail(function() {
                alert("Error Loading Characters");
            });
    },
    setPosition : function(position) {
        geo_options = {
            enableHighAccuracy : true,
            maximumAge : 30000,
            timeout : 27000
        };
        navigator.geolocation.getCurrentPosition(function(position) {
            viewModel.userLat(position.coords.latitude);
            viewModel.userLng(position.coords.longitude);
        }, geo_error , geo_options);
    },
    locCheck : function() {
        loc = new google.maps.LatLng(viewModel.userLat(), viewModel.userLng())
        viewModel.eventLocation($("#loc").text());
        distance.getDistanceMatrix(
          {
            origins: [loc],
            destinations: [viewModel.eventLocation()],
            travelMode : 'DRIVING'
          }, callback);
        function callback(response, status) {
            if (status == 'OK') {
                console.log(status);
                console.log(response);
                meters = response.rows[0].elements[0].distance.value;
                console.log(meters);

                if(meters < 1000) {
                  data = $("#points").text()
                  $.post("http://localhost:5000/api/check_in/", {
                    points : data
                  })
                  .done(function(data) {
                    console.log(data);
                  })
                  .fail(function() {
                    console.log("Error");
                  })
                } else {
                    points = false;
                    return alert("You're not close enough to the event.")
                }
            }return console.log(points);
        }

    }
};
ko.applyBindings(viewModel);

if ("geolocation" in navigator) {
  console.log('geolocation is available');
} else {
   console.log('geolocation IS NOT available');
}
