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
    }
};
ko.applyBindings(viewModel);
