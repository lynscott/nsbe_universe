//Marvel api

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


var viewModel = {
    userInput : ko.observable(''),
    characterName : ko.observable(''),
    characterDesc : ko.observable(''),
    characterImage : ko.observable(''),
    getInfo : function() {

        var base_url = 'https://gateway.marvel.com:443/v1/public/characters?';
        var api = '&apikey=194e9e5d5fcffb43dadcb84dc251c2b4';
        var character = 'name='+this.userInput();

        var url = base_url+character+api;
        //Request Marvel Character Info
        $.getJSON(url)
            .done(function(result) {
                var data = result.data.results[0];

                userCharacter = new MarvelCharacter(data);
                viewModel.characterName(userCharacter.name);
                viewModel.characterDesc(userCharacter.description);
                viewModel.characterImage(userCharacter.thumbnail.path+"."
                                    +userCharacter.thumbnail.extension);
                return userCharacter;


            }).fail(function() {
                alert("Error Loading Characters");
            });
    }
};
ko.applyBindings(viewModel);
