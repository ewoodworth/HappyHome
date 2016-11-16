// BELOW THIS LINE, SCRIPT CAME FROM LOGINBAR.HTML

  function onSignIn(googleUser) {
    // Useful data for your client-side scripts:
    var profile = googleUser.getBasicProfile();
    console.log("ID: " + profile.getId()); // Don't send this directly to your server!
    console.log('Full Name: ' + profile.getName());
    console.log('Given Name: ' + profile.getGivenName());
    console.log('Family Name: ' + profile.getFamilyName());
    console.log("Image URL: " + profile.getImageUrl());
    console.log("Email: " + profile.getEmail());

    // The ID token you need to pass to your backend:
    var id_token = googleUser.getAuthResponse().id_token;
    console.log("ID Token: " + id_token);
  };

// BELOW THIS LINE IS FROM DASHBOARD.HTML

  // var options = { responsive: true };

  // var ctx_donut = $("#donutChart").get(0).getContext("2d");

  // $.get("/user-contributions.json", function (data) {
  //     var myDonutChart = new Chart(ctx_donut, {
  //                                             type: 'doughnut',
  //                                             data: data,
  //                                             options: options
  //                                           });
  //     $('#donutLegend').html(myDonutChart.generateLegend());
  // });


// BELOW THIS LINE IS FROM NEWCHORE.HTML
    // a general function to update the secondary pulldown
    function addsecondElementOptions(color) {

      // get array for days of the week
      var dow = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

      // get the secondary pulldown and empty it
      var secondElement = $("#secondary-element");
      secondElement.empty();
      $("#secondary-label").html("");

      // add an option foreach possibility in form-initial
      if ($("#initial-pulldown").val() == 'daily') {
      } else if ($("#initial-pulldown").val() == 'weekly') {
          for (var i = 0; i < dow.length; i++) {
        secondElement.append(" <input type='checkbox' name='days_weekly' value=" + dow[i] + ">" + dow[i]);
        };
      $("#secondary-label").html("Which days does it need to happen?");
      } else if ($("#initial-pulldown").val() == 'monthly') {
        secondElement.append("By day <input type='number' name='date_monthly' min='1' max='31'> of the month.");
      }

      // finally, unhide the second pulldown
      $('#secondary-form-group').show();
      $('#time-form-group').show();

    };

    // event handler watching for change to the main pulldown
    var mainPull = $("#initial-pulldown"); 
    mainPull.change(function() {

      // update the secondary pulldown if there's a value
      if (mainPull.val() !== "") {
        addsecondElementOptions(mainPull.val());
      // otherwise, hide it
      } else {
        $('#secondary-form-group').hide();
      }
    });

// BELOW THIS LINE IS FROM TAKEACHORE.HTML
  $(document).ready(function() {
    // event handler for change to the main pulldown
    var mainPull = $("#initial-pulldown");

    mainPull.change(function() {
      console.log("I'm awake!");
      // sendFormIn();
      // update the secondary menu if there's a value
      if (mainPull.val() !== "") {
        sendFormIn();
      // otherwise, hide it
      } else {
        $('#secondary-form-group').hide();
        $('aggree-button-div').hide();
      }
    });

    function agreeToWeeklyChore() {
        var agreementsInput = {
          "daysagreed": $('#Monday-checkbox').is(":checked").toString() + "|" +
                  $('#Tuesday-checkbox').is(":checked").toString() + "|" +
                  $('#Wednesday-checkbox').is(":checked").toString() + "|" +
                  $('#Thursday-checkbox').is(":checked").toString() + "|" +
                  $('#Friday-checkbox').is(":checked").toString() + "|" +
                  $('#Saturday-checkbox').is(":checked").toString() + "|" +
                  $('#Sunday-checkbox').is(":checked").toString(),
          "chore_id": $('#initial-pulldown').val()
        };

      $.post("/take_weekly_agreements", 
      agreementsInput,
      function() { $('#secondary-form-group').empty();}
      );
    }

    function agreeToMonthlyChore(){
        var agreementsInput = {
          "date_monthly": $('#date_monthly-checkbox').is(":checked").toString(),
          "chore_id": $('#initial-pulldown').val()
        };
      

      $.post("/take_monthly_agreements", 
      agreementsInput,
      function() { $('#secondary-form-group').empty();}
      );
    }


    function successFunction(incoming){
      $("#secondary-form-group").empty();
      console.log(incoming.days_left)
      console.log(incoming.days_left.length)
      if (incoming.occurance == 'daily'||incoming.occurance == 'weekly') {
        for (var i = 0; i < incoming.days_left.length; i++) {
          console.log(incoming.days_left[i])
          // $("#secondary-form-group").append("Hi! *");
          $("#secondary-form-group").append(" <input type='checkbox' id='" + incoming.days_left[i] + "-checkbox' name = 'day' value=" + incoming.days_left[i] + ">" + incoming.days_left[i][0] + incoming.days_left[i][1]);
          };
          $("#secondary-form-group").append(" <button id='weekly-agree-button'> I'll Take These Days!</button>")
      } else if (incoming.occurance == 'monthly') {
        $("#secondary-form-group").append(" <input type='checkbox' id='date_monthly-checkbox' name = 'date_monthly' value='checkbox'>" + incoming.date_monthly);
        $("#secondary-form-group").append(" <button id='monthly-agree-button'> I'll Do This!</button>");
      }

      $("#weekly-agree-button").click(function() { 
                         agreeToWeeklyChore();
      });
      $("#monthly-agree-button").click(function() { 
             agreeToMonthlyChore();
      });
    }

      $('#secondary-form-group').show();

    function sendFormIn() {
        // evt.preventDefault();
        var formInputs = {
          "form_chore_id": $("#initial-pulldown").val()
        }

        $.post("/takechoreform", 
            formInputs,
            successFunction
            );
    }

  });
// ^ THIS IS FROM THE DOCUMT READY TAG AT THE TOP


// BELOW THIS LINE IS FROM 
function geocodeAddress(geocoder, resultsMap) {
  var address = document.getElementById('address').value;
  geocoder.geocode({'address': address}, function(results, status) {
    if (status === 'OK') {
      resultsMap.setCenter(results[0].geometry.location);
      var marker = new google.maps.Marker({
        map: resultsMap,
        position: results[0].geometry.location
      });
    } else {
      alert('Geocode was not successful for the following reason: ' + status);
    }
  });
}