"use strict";
/**
 * Facebook SDK asynchronous client
 * 2015, by Cesar Anton Dorantes @reicek
 * for https://platzi.com/blog
 * demo: https://googledrive.com/host/0B_RClkFMLkcpdlZfX0pJYjFaUjQ/
 * Github: https://github.com/reicek/Facebook-SDK-asynchronous-client
 * This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License. 
 * To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/
 **/
// *******************************************************
//    Variables Globales
// *******************************************************
//  Facebook App ID
var facebookAppID = document.getElementById('facebook-login-button').getAttribute("appId");
// -------------------------------------------------------
//  Facebook User Data
var facebookUser = {};
//  Child objects:
//    facebookUser.id
//    facebookUser.name
//    facebookUser.first_name
//    facebookUser.last_name
//    facebookUser.link
//    facebookUser.gender
//    facebookUser.locale
//    facebookUser.timezone
//    facebookUser.updated_time
//    facebookUser.verified
// -------------------------------------------------------
// *******************************************************
//    Callbacks
// *******************************************************
//  Función a llamar cuando el login se realiza correctamente
var Facebook_correctLogin = function () {
  //  Obtener los datos del usuario
  FB.api('/me', function(response) {
    // Guardar los datos en una variable global
    facebookUser = response;
    // Esconder el boton de login
    document.getElementById('facebook-login-button').style.display = "none";
    // Saludar al usuario
    if (document.getElementById('fbStatus')){
      document.getElementById('fbStatus').innerHTML = '¡Bienvenido ' + facebookUser.name + '!'
    }
    // Mostrar los datos en la consola
    console.log('____________________');
    console.log('Bienvenido ' + facebookUser.name);
    console.log('Tus datos:');
    console.log(facebookUser);
    console.log('____________________');
  })
};
//  Función a llamar cuando la persona esta conectada a Facebook, pero no a tu aplicación
var Facebook_notAuthorized  = function () {
  if (document.getElementById('fbStatus')){
    document.getElementById('fbStatus').innerHTML = 'Es necesario conectarse a la aplicación.'
  }
};
//  Función a llamar si la persona no esta conectada a Facebook
var Facebook_notConnected = function () {
  if (document.getElementById('fbStatus')){
    document.getElementById('fbStatus').innerHTML = 'Es necesario estar conectado a Facebook.'
  }
};
//  Iniciada de forma asíncrona por FB.getLoginStatus()
var statusChangeCallback  = function (response) {
  console.log('____________________');
  console.log('statusChangeCallback');
  console.log(response);
  console.log('____________________');
  //  Login y autorización correctas
  if (response.status === 'connected') {
    Facebook_correctLogin();
  //  Login correcto, sin autorización
  } else if (response.status === 'not_authorized') {
    Facebook_notAuthorized();
  } else {
  //  Usuario no conectado a Facebook
    Facebook_notConnected();
  }
};
// *******************************************************
//    Iniciar la SDK de Facebook de forma asíncrona
// *******************************************************
window.fbAsyncInit  = function() {
  //  Ajuste de opciones
  FB.init({
    appId      : facebookAppID,
    cookie     : true,
    xfbml      : true,
    version    : 'v2.2'
  });
  //  Llamar statusChangeCallback() al iniciar sesión
  FB.getLoginStatus(function(response) {
    statusChangeCallback(response);
  })
};
// *******************************************************
//    Cargar la SDK de Facebook de foma asíncrona
// *******************************************************
(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js";
  fjs.parentNode.insertBefore(js, fjs)
}(document, 'script', 'facebook-jssdk'))
// *******************************************************




// // FACEBOOK
//   $.ajaxSetup({ cache: true });
//   $.getScript('//connect.facebook.net/en_US/sdk.js', function(){
//     FB.init({
//       appId: '1231432380263610',
//       xfbml: true,
//       version: 'v2.7' // or v2.1, v2.2, v2.3, ...
//     });
//     $('#loginbutton').removeAttr('disabled');
//     FB.getLoginStatus(updateStatusCallback);
//     });

//   $('#loginbutton').click(FB.getLoginStatus(updateStatusCallback));

//   function updateStatusCallback(){
//   // console.log(thing);
//   $.post("/takefbuser",
//       thing);
//   }

// // GOOGLE
//   // function onSignIn(googleUser) {
//   //   var profile = googleUser.getBasicProfile();
//   //   var {'id_token': googleUser.getAuthResponse().id_token,
//   //   'Name': profile.getName(),
//   //   'Email': profile.getEmail()}


//   //   $.post("/tokensignin",
//   //       id_token);
//   // }

//   // // var xhr = new XMLHttpRequest();
//   // // xhr.open('POST', 'http://localhost:5000/tokensignin');
//   // // xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
//   // // xhr.onload = function() {
//   // //   console.log('Signed in as: ' + xhr.responseText);
//   // // };
//   // // xhr.send('idtoken=' + id_token);

//   // // GOOGLE
//   // function onSignIn(googleUser) {
//   //   // Useful data for your client-side scripts:
//   //   var profile = googleUser.getBasicProfile();
//   //   console.log("ID: " + profile.getId()); // Don't send this directly to your server!
//   //   console.log('Full Name: ' + profile.getName());
//   //   console.log('Given Name: ' + profile.getGivenName());
//   //   console.log('Family Name: ' + profile.getFamilyName());
//   //   console.log("Image URL: " + profile.getImageUrl());
//   //   console.log("Email: " + profile.getEmail());

//   //   // The ID token you need to pass to your backend:
//   //   var id_token = googleUser.getAuthResponse().id_token;
//   //   console.log("ID Token: " + id_token);
//   // };