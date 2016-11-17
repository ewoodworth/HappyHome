// BELOW THIS LINE IS FROM DASHBOARD.HTML

  var options = { responsive: true };

  var ctx_donut = $("#donutChart").get(0).getContext("2d");

  $.get("/user-contributions.json", function (data) {
      var myDonutChart = new Chart(ctx_donut, {
                                              type: 'doughnut',
                                              data: data,
                                              options: options
                                            });
      $('#donutLegend').html(myDonutChart.generateLegend());
  });