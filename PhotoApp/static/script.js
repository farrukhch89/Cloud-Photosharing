'use strict';

window.addEventListener('load', function () {
    // get the signout button and add an onclick listener to it
    document.getElementById('sign-out').onclick = function() {
        // ask firebase to sign out the user
        firebase.auth().signOut();
    };

    // variable that will be used to determine how firebase will show its UI
    var uiConfig = {
        signInSuccessUrl: '/',  // where in the application we will redirect to on a successful user login
        signInOptions: [
            // permit google authentication and email authentication
            firebase.auth.GoogleAuthProvider.PROVIDER_ID,
            firebase.auth.EmailAuthProvider.PROVIDER_ID
        ]
    };

    // javascript that will react to whenever the firebase authentication state changes
    firebase.auth().onAuthStateChanged(function(user) {
        // determine if a user is signed in or not
        if(user) {
            // user is signed in so display the sign out button, and login info
            document.getElementById('sign-out').hidden = false;
            document.getElementById('login-info').hidden = false;

            // log the user login to console for debug purposes with the name and email address
            console.log('Signed in as ${user.displayName} (${user.email})');

            // get the id token for the user and set it as a cookie so we can maintain a session
            user.getIdToken().then(function(token) {
                document.cookie = "token=" + token;
            });
        } else {
            // there is no user signed in so initialise a firebase UI widget and set it on the approriate part of the template
            var ui = new firebaseui.auth.AuthUI(firebase.auth());
            ui.start('#firebase-auth-container', uiConfig);

            // hide the signout and login-info fields and clear the token
            document.getElementById('sign-out').hidden = true;
            document.getElementById('login-info').hidden = true;
            document.cookie = "token=";
        }
    }, function(error) {
        // if something goes wrong then log the error to console and state the user could not be logged in
        console.log(error);
        alert('Unable to log in: ' + error);
    });
    
});
