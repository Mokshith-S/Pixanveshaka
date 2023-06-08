const form = document.getElementById('form');
const Fname = document.getElementById('Fname');
const username = document.getElementById('username');
const email = document.getElementById('email');
const phoneNumber= document.getElementById('phoneNumber');
const password = document.getElementById('password');


form.addEventListener('submit', e => {
    e.preventDefault();
    
    validateInputs();
});

const setError = (element, message) => {
    const inputControl = element.parentElement;
    const errorDisplay = inputControl.querySelector('.error');

    errorDisplay.innerText = message;
    inputControl.classList.add('error');
    inputControl.classList.remove('success');
};

const setSuccess = element => {
    const inputControl = element.parentElement;
    const errorDisplay = inputControl.querySelector('.error');

    errorDisplay.innerText = '';
    inputControl.classList.add('success');
    inputControl.classList.remove('error');
};

const isValidEmail = email => {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
};


 const s =/^[A-Za-z]+$/;
 
 const d =/^[A-Za-z]+$/;
 var cars = new Array(5).fill(false);
const validateInputs = () => {
    var count = 0;
    const FnameValue =Fname.value.trim();
    const usernameValue = username.value.trim();
    const emailValue = email.value.trim();
    const phoneNumberValue =phoneNumber.value.trim();
    const passwordValue = password.value.trim();
    

    if(FnameValue === ''){
        setError(Fname,'name is required');
        // cars[0] = false;
    }else if ((FnameValue.length <= 2 ) || (FnameValue.length > 20)) {
        setError(Fname, 'Name lenght must be between  2 and 10');
    }else if(!FnameValue.match(s)){
        setError(Fname, 'Name should be in alphabet');
    }
        else{ 
        setSuccess(Fname);
        cars[0] = true;
    }
    if(usernameValue === '') {
        setError(username, 'Username is required');
    } else if((usernameValue.length <= 4) || (usernameValue.length > 6)) {
        setError(username, 'Username must be between 4 and 6.');
    }
     else if(!usernameValue.match(d)) {
            setError(username,'username should be in alphabet');
        }
            else{
            setSuccess(username);
            cars[0] = true;
        } 

    if(emailValue === '') {
        setError(email, 'Email is required');
    } else if (!isValidEmail(emailValue)) {
        setError(email, 'Provide a valid email address');
    } else {
        setSuccess(email);
        cars[0] = true;
    }
    
    if(phoneNumberValue == ''){
       setError(phoneNumber,'Phone number is required');
    }else if(phoneNumberValue.length !=10 ) {
        setError(phoneNumber, 'Number must be 10 digit');
    }else{
        setSuccess(phoneNumber);
        cars[0] = true;
    }

    if(passwordValue === '') {
        setError(password, 'Password is required');
    } else if ((passwordValue.length <= 4) || (passwordValue.length >8)) {
        setError(password, 'Password length must be between 4 and 8')
    } else {
        setSuccess(password);
        cars[0] = true;
    }
    console.log(count);
    
        for(var i = 0; i < 5; i++) {
            if(cars[i]) {
                count++;
            }
        }
        if (count == 5) {
            alert("fre");
                    window.location("/signup");
            }
};
