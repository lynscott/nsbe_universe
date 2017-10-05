//Marvel api
var Character = function(result) {
    this.id = result.id;
    this.name = result.name;
    this.description = result.description|| "n/a";
    this.thumbnail = result.thumbnail;
};


marvelArray = []

var base_url = 'https://gateway.marvel.com:443/v1/public/characters?orderBy=name&apikey=194e9e5d5fcffb43dadcb84dc251c2b4';
var endpoint = '';



var url = base_url;

//Request Foursquare marker info
$.getJSON(url)
    .done(function(result) {
        var characterList = result.data.results;

        self.charactersArray = [];

        //Push each venue into ko array and convert foursqaure venue data into the object data that you want
        characterList.forEach(function(result) {
            marvelArray.push(new Character(result));
        });

        //Create google markers for each venue, push markers into global Markers array

    }).fail(function() {
        alert("Error Loading Characters");
    });
