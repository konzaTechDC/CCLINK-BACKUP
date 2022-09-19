
// var attempt = 3;

var userObj = [
    {
        'userID': 1,
        'email': 'user1@gmail.com',
        'password': '12345'
    },
    {
        'userId': 2,
        'email': 'user2@gmail.com',
        'password': 'test123'
    },
    {
        'userId': 3,
        'email': 'user3@gmail.com',
        'password': 'test1234'
    }

];

function validateLogin(){
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;

    // console.log('your email is ' + email + ' and password is ' + password)

    for (var i = 0; i< userObj.length; i++){
        if (email == userObj[i].email && password == userObj[i].password){
            // window.location='index.html';
            // return;
            console.log(`Your email is ${email}`);
        }
    }

    // if (username == 'userA' && password == '1234')
    // {
    //     window.location = '../Compliance/index.html';
    //     return ;
    // } else 
    // {
    //     attempt --;
    //     alert(`You have ${attempt} left to try!`);

    //     if (attempt == 0){
    //         document.getElementById('email').disabled = true;
    //         document.getElementById('password').disabled = true;
    //         document.getElementById('login').disabled = true;

    //         return false;
    //     }
    // }
}
