
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
  alertify.alert("Sorry, no position available.");
}


$.getJSON("http://localhost:5000/users/JSON")
        .done(function(data){
            console.log(data);
            users=data.users
            events=data.events
            return data;
        }).fail(function() {
            alertify.error("Error getting user data");
        });

start = $("#date").text().slice(-10) + ' ' + $("#start").text().slice(-8)
end = $("#date").text().slice(-10) + ' ' + $("#end").text().slice(-8)

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
    userLat : ko.observable(''),
    userLng : ko.observable(''),
    eventLocation : ko.observable(''),
    startTime : ko.observable(moment(start)),
    endTime : ko.observable(moment(end)),
    disable: ko.observable(false),
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
                alertify.error("Error Loading Characters");
            });
    },
    setPosition : ko.computed(function() {
        geo_options = {
            enableHighAccuracy : true,
            maximumAge : 30000,
            timeout : 27000
        };
        navigator.geolocation.watchPosition(function(position) {
            viewModel.userLat(position.coords.latitude);
            viewModel.userLng(position.coords.longitude);
        }, geo_error , geo_options);
    }),
    checkIn : function() {
        loc = new google.maps.LatLng(viewModel.userLat(), viewModel.userLng())
        viewModel.eventLocation(events.filter(events => events.id== parseInt($("#event").text().slice(8))));
        distance.getDistanceMatrix(
          {
            origins: [loc],
            destinations: [viewModel.eventLocation()[0].address],
            travelMode : 'DRIVING'
          }, callback);
        function callback(response, status) {
            if (status == 'OK') {
                console.log(status);
                meters = response.rows[0].elements[0].distance.value;
                console.log(meters);

                if(meters < 1000) {
                  points = parseInt($("#points").text().slice(7));
                  event_id= parseInt($("#event").text().slice(8));

                  $.post("http://localhost:5000/api/check_in/", {
                    data : {"points": points, "event_id":event_id},
                    dataType : "application/json",
                  })
                  .done(function() {
                    viewModel.disable(true);
                    return alertify.success("Check-in successful!");
                  })
                  .fail(function() {
                    console.log("Error");
                  })
                } else {
                    points = false;
                    return alertify.error("You're not close enough to the event.");
                }
            }
        }

    },
    checkDate : function() {
      if(viewModel.startTime() < moment() && viewModel.endTime() > moment()) {
        return viewModel.checkIn();
      }else if (viewModel.startTime() > moment()) {
        return alertify.alert("This event hasn't started yet!");
      }else if (viewModel.endTime() < moment()) {
        return alertify.alert("This event has ended.")
      }
    }
};
ko.applyBindings(viewModel);

if ("geolocation" in navigator) {
  console.log('geolocation is available');
} else {
   console.log('geolocation IS NOT available');
}
