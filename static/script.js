// Created by Andy Then

function loadDoc(url, func){
    let xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (xhttp.status != 200) {
            console.log("Error");
        } else {
            if (xhttp.response === null) {
                console.error("Error");
                return;
            }
            func(xhttp.response);
        }
    }
    xhttp.open("GET", url);
    xhttp.responseType = "json"; 
    xhttp.send();
}

function login(){
    let txtEmail = document.getElementById("txtEmail");
    let txtPassword = document.getElementById("txtPassword");

    if (txtEmail.value == '' || txtPassword.value == '') {
        alert("email and password cannot be blank.");
        return;
    }

    let url = "/login?email=" + encodeURIComponent(txtEmail.value) + 
              "&password=" + encodeURIComponent(txtPassword.value);

    let chkRemember = document.getElementById("chkRemember");
    if(chkRemember.checked){
        url += "&remember=yes";
    }else{
        url += "&remember=no";
    }

    loadDoc(url, login_response);
}

function login_response(response) {
    let result = response.result;
    if(result != "OK") {
        alert(result);
    }
    else{
        window.location.replace("/feed");
    }
}

function create_profile() {
    let xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (xhttp.status != 200) {
            console.log("Error");
        } else {
            create_profile_response(JSON.parse(xhttp.response));
        }
    }

    xhttp.open('POST','/create_profile',true);
    var formData = new FormData();
    email = document.getElementById('txtEmail').value
    if (email == '' || document.getElementById('txtPassword').value == '') {
        alert("email and password can not be blank.");
        return;
    }
    //check if email has @ and .
    let hasAt = email.includes("@");
    let hasDot = email.includes(".");
    if(hasAt == false || hasDot == false){
        alert("email must have a @ and a .");
        return;
    }

    formData.append("username", document.getElementById('txtUsername').value);
    formData.append("email", email);
    formData.append("password", document.getElementById('txtPassword').value);

    xhttp.send(formData);
}

// Ths is going to automatically log the user in after sign up
function create_profile_response(response) {
    if (response.error === 'email_exists') {
        alert('This email is already in use');
        return;
    }
    
    if (response.error) {
        alert(response.error);
        return;
    }

    // Auto login
    let txtEmail = document.getElementById('txtEmail');
    let txtPassword = document.getElementById('txtPassword');
    
    let url = "/login?email=" + encodeURIComponent(txtEmail.value) + 
              "&password=" + encodeURIComponent(txtPassword.value);
              
    loadDoc(url, (loginResponse) => {
        if (loginResponse.result === "OK") {
            window.location.replace("/feed");
        } else {
            alert("Account created but automatic login failed. Please log in manually.");
            window.location.replace("/login");
        }
    });
}

function list_posts(){
    let url = '/listposts'
    loadDoc(url, list_posts_response)
}

function list_posts_response(response){
    let posts = response["posts"];
    
    temp = "";

    for (let i = 0; i < posts.length; i++){
        upload = posts[i];

        temp += "<div class=\"post_container\">";
        temp += "<div class=\"post_username\">" + "<a href=\"/profile/" + upload["username"] + "\">" + upload["username"] + "</a>" + "</div>";
        temp += "<div class=\"post_date\">" + upload["date"] + "</div>";
        temp += "<div class=\"post_text\">" + upload["text"] + "</div>";
        temp += "<div class=\"replies_button\">" + "<a href=\"/replies/" + upload["pid"] + "\">" + "reply" + "</a>" + "</div>";
        temp += "</div>";
    }

    let divResults = document.getElementById("divResults");
    divResults.innerHTML = temp;
}

function delete_post(pid) {
    let xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (xhttp.status != 200) {
            console.error("Error: ", xhttp.responseText);
        } else {
            window.location.reload();
        }
    };

    xhttp.open('POST', '/deletepost', true);
    let formData = new FormData();
    formData.append("pid", pid);

    xhttp.send(formData);
}

function list_users_posts(uid){
    let url = "/list_users_posts?uid=" + uid;
    loadDoc(url, list_users_posts_response);
}

function list_users_posts_response(response){
    let posts = response["posts"];

    let temp = "";

    for (let i = 0; i < posts.length; i++){
        let upload = posts[i];

        temp += "<div class=\"post_container\">";
        temp += "<div class=\"post_username\"><a href=\"/profile/" + upload["username"] + "\">" + upload["username"] + "</a></div>";
        temp += "<div class=\"post_date\">" + upload["date"] + "</div>";
        temp += "<div class=\"post_text\">" + upload["text"] + "</div>";
        temp += "<button onclick='delete_post(\"" + upload["pid"] + "\")'>Delete</button>";
        temp += "<a href=\"/replies/" + upload["pid"] + "\" class=\"replies_button\">Reply</a>";
    }

    let divResults = document.getElementById("divResults");
    divResults.innerHTML = temp;
}

function list_replies(parent_pid) {
    let url = '/list_replies?parent_pid=' + parent_pid
    loadDoc(url, list_replies_response)
}

function list_replies_response(response){
    let replies = response["results"];

    temp = "";

    for (let i = 0; i < replies.length; i++){
        upload = replies[i];

        temp += "<div class=\"reply_container\">";
        temp += "<div class=\"reply_username\">" + upload["username"] + "</div>";
        temp += "<div class=\"reply_date\">" + upload["date"] + "</div>";
        temp += "<div class=\"reply_text\">" + upload["text"] + "</div>";
        temp += "</div>" + "<br>";
    }

    let divResults = document.getElementById("divResults");
    divResults.innerHTML = temp;
}

function post_reply(){
    let xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (xhttp.status != 200) {
            console.log("Error");
        } else {
            post_reply_response(JSON.parse(xhttp.response));
        }
    }

    xhttp.open('POST','/post_reply',true);
    var formData = new FormData();
    formData.append("parent_pid", document.getElementById('parent_pid').value);
    formData.append("text", document.getElementById('text').value);
    xhttp.send(formData);
}

function post_reply_response(response) {
    location.reload();
}

function post() {
    let xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (xhttp.status != 200) {
            console.log("Error");
        } else {
            post_response(JSON.parse(xhttp.response));
        }
    }

    xhttp.open('POST','/post',true);
    var formData = new FormData();
    formData.append("text", document.getElementById('text').value);
    xhttp.send(formData);
}

function post_response(response) {
    location.reload();
}

function logout(){
    window.location.href = '/logout';
}

function upload_file() {
    let xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (xhttp.status != 200) {
            console.log("Error");
        } else {
            upload_file_response(JSON.parse(xhttp.response));
        }
    }

    xhttp.open('POST','/uploadfile',true);
    var formData = new FormData();
    formData.append("file", document.getElementById('file').files[0]);
    xhttp.send(formData);
}

function upload_file_response(response) {
    location.reload();
}