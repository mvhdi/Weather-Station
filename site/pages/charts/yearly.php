
<!doctype html>
<html>
    <head>
        
    </head>
        <div class="btn-group btn-group-justified">
  <a href="#" class="btn btn-default">Weekly</a>
  <a href="#" class="btn btn-default">Monthly</a>
  <a href="#" class="btn btn-default">Yearly</a>
</div>
    <h2>  <span> <i class="far fa-chart-bar"></i> </span> Yearly Charts  </h2>
    <div class="panel panel-default"  >
        <div id="current-conditions" class="panel-collapse collapse in" >
            <div class="panel-body" >

                <body> 



                            <div class="container-fluid"  > 

                                <canvas id="myChart20" ></canvas>

                                    <script src="Chart.js"></script>
                                    <script>


                                        Chart.defaults.global.defaultFontColor = 'rgba(255, 255, 255, 0.8)';
                                        Chart.defaults.global.defaultFontSize = 18;
                                        Chart.defaults.global.defaultFontFamily = 'Helvetica Neue';
                                        Chart.defaults.global.defaultFontStyle = 'normal';


                                        <?php
                                            $labelpoints = array("6/21", "6/22", "6/23", "6/24", "6/25", "6/26", "6/27");
                                            $datapointsOne = array(65,79,85,93,56,87, 77);

                                            $datapointsTwo =  array(55,59,75,73,26,47, 57);
                                        ?>


                                        var labelValuesOne = <?php echo json_encode($labelpoints ) ?>;
                                        var dataValuesOne = <?php echo json_encode($datapointsOne) ?>;
                                        var dataValuesTwo = <?php echo json_encode($datapointsTwo) ?>;


                                        var ctx = document.getElementById("myChart20").getContext('2d');
                                        var myChart = new Chart(ctx, {
                                            type: 'line',
                                            
                                            data: {
                                                labels: labelValuesOne,
                                                datasets: [{
                                                    label: 'Temperature°F High (Week)',
                                                    fill: false,
                                                    lineTension: 0,
                                                    data: dataValuesOne,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: [
                                                        'rgba(255, 99, 132, 0.2)'
                                                    ],
                                                    borderColor: [
                                                    'rgba(255,99,132,1)'
                                                    ],
                                                    borderWidth: 1,
                                                },{
                                                    label: 'Temperature°F Low (Week)',
                                                    fill: false,
                                                    lineTension: 0.2,
                                                    data: dataValuesTwo,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: [
                                                        'rgba(99, 132, 255, 0.2)'
                                                    ],
                                                    borderColor: [
                                                    'rgba(99,132,255,1)'
                                                    ],
                                                    borderWidth: 1,
                                                }
                                                ]
                                            },
                                            options: {
                                                scales: {
                                                    yAxes: [{
                                                        ticks: {
                                                            beginAtZero:true
                                                        },
                                                        display: true,
                                                        gridLines: {
                                                            display: true,
                                                            color: 'rgba(255, 255, 255, 0.3)'
                                                        },
                                                    }],
                                                    xAxes: [{
                                                        display: true,
                                                        gridLines: {
                                                            display: true,
                                                            color: 'rgba(255, 255, 255, 0.3)'
                                                        },
                                                    }],
                                                }
                                            }
                                        });


                                    </script>
                                </canvas>

                                <h3> &nbsp;</h3>

                            <div class="container-fluid"  > 

                                <canvas id="myChart21" ></canvas>

                                    <script src="Chart.js"></script>
                                    <script>


                                        Chart.defaults.global.defaultFontColor = 'rgba(255, 255, 255, 0.8)';
                                        Chart.defaults.global.defaultFontSize = 18;
                                        Chart.defaults.global.defaultFontFamily = 'Helvetica Neue';
                                        Chart.defaults.global.defaultFontStyle = 'normal';


                                        <?php
                                            $labelpoints = array("5/27","5/28","5/29","6/30","5/31","6/1", "6/2", "6/3","6/4", "6/5", "6/6", "6/7", "6/8", "6/9","6/10", "6/11", "6/12", "6/13","6/14", "6/15", "6/16", "6/17", "6/18", "6/19","6/20","6/21", "6/22", "6/23", "6/24", "6/25", "6/26", "6/27");
                                            $datapointsOne = array(65,79,85,93,56,87, 77,65,79,85,93,56,87, 77,65,79,85,93,56,87, 77,65,79,85,93,56,87, 77,65,79,85,93);

                                            $datapointsTwo =  array(55,59,75,73,26,47, 57,55,59,75,73,26,47, 57,55,59,75,73,26,47, 57,55,59, 75,73,26,47, 57,55,59,75,73);
                                        ?>


                                        var labelValuesOne = <?php echo json_encode($labelpoints ) ?>;
                                        var dataValuesOne = <?php echo json_encode($datapointsOne) ?>;
                                        var dataValuesTwo = <?php echo json_encode($datapointsTwo) ?>;


                                        var ctx = document.getElementById("myChart21").getContext('2d');
                                        var myChart = new Chart(ctx, {
                                            type: 'line',
                                            
                                            data: {
                                                labels: labelValuesOne,
                                                datasets: [{
                                                    label: 'Temperature°F High (Month)',
                                                    fill: false,
                                                    lineTension: 0,
                                                    data: dataValuesOne,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: [
                                                        'rgba(255, 99, 132, 0.2)'
                                                    ],
                                                    borderColor: [
                                                    'rgba(255,99,132,1)'
                                                    ],
                                                    borderWidth: 1,
                                                },{
                                                    label: 'Temperature°F Low (Month)',
                                                    fill: false,
                                                    lineTension: 0,
                                                    data: dataValuesTwo,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: [
                                                        'rgba(99, 132, 255, 0.2)'
                                                    ],
                                                    borderColor: [
                                                    'rgba(99,132,255,1)'
                                                    ],
                                                    borderWidth: 1,
                                                }
                                                ]
                                            },
                                            options: {
                                                scales: {
                                                    yAxes: [{
                                                        ticks: {
                                                            beginAtZero:true
                                                        },
                                                        display: true,
                                                        gridLines: {
                                                            display: true,
                                                            color: 'rgba(255, 255, 255, 0.3)'
                                                        },
                                                    }],
                                                    xAxes: [{
                                                        display: true,
                                                        gridLines: {
                                                            display: true,
                                                            color: 'rgba(255, 255, 255, 0.3)'
                                                        },
                                                    }],
                                                }
                                            }
                                        });


                                    </script>
                                </canvas>
                                <h3> &nbsp;</h3>

                            <div class="container-fluid"  > 

                                <canvas id="myChart22" ></canvas>

                                    <script src="Chart.js"></script>
                                    <script>


                                        Chart.defaults.global.defaultFontColor = 'rgba(255, 255, 255, 0.8)';
                                        Chart.defaults.global.defaultFontSize = 18;
                                        Chart.defaults.global.defaultFontFamily = 'Helvetica Neue';
                                        Chart.defaults.global.defaultFontStyle = 'normal';


                                        <?php
                                            $labelpoints = array("1AM","2AM","3AM","4AM","5AM","6AM", "7AM", "8AM","9AM", "10AM", "11AM", "12AM", "1PM", "2PM","3PM", "4PM", "5PM", "6PM","7PM", "8PM", "9PM", "10PM", "11PM", "12PM");
                                            $datapointsOne = array(25,26,35,33,36,40,55,65,42,65,21,56,62,  42,65,79,85,93,56,87,77,65,79,85,93,);

                                            
                                        ?>


                                        var labelValuesOne = <?php echo json_encode($labelpoints ) ?>;
                                        var dataValuesOne = <?php echo json_encode($datapointsOne) ?>;
                                        var dataValuesTwo = <?php echo json_encode($datapointsTwo) ?>;


                                        var ctx = document.getElementById("myChart22").getContext('2d');
                                        var myChart = new Chart(ctx, {
                                            type: 'bar',
                                            
                                            data: {
                                                labels: labelValuesOne,
                                                datasets: [{
                                                    label: 'Barometric Pressure (24 Hours)',
                                                    fill: true,
                                                    lineTension: 0.2,
                                                    data: dataValuesOne,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: [
                                                        'rgba(132, 255, 99, 0.2)',
                                                        'rgba(132, 255, 99, 0.2)',
                                                        'rgba(132, 255, 99, 0.2)',
                                                        'rgba(132, 255, 99, 0.2)',
                                                        'rgba(132, 255, 99, 0.2)',
                                                        'rgba(132, 255, 99, 0.2)',
                                                        'rgba(132, 255, 99, 0.2)',
                                                        'rgba(132, 255, 99, 0.2)',
                                                        'rgba(132, 255, 99, 0.2)',
                                                        'rgba(132, 255, 99, 0.2)',
                                                        'rgba(132, 255, 99, 0.2)',
                                                        'rgba(132, 255, 99, 0.2)',



                                                        'rgba(255, 99, 132, 0.2)',
                                                        'rgba(255, 99, 132, 0.2)',
                                                        'rgba(255, 99, 132, 0.2)',
                                                        'rgba(255, 99, 132, 0.2)',
                                                        'rgba(255, 99, 132, 0.2)',
                                                        'rgba(255, 99, 132, 0.2)',
                                                        'rgba(255, 99, 132, 0.2)',
                                                        'rgba(255, 99, 132, 0.2)',
                                                        'rgba(255, 99, 132, 0.2)',
                                                        'rgba(255, 99, 132, 0.2)',
                                                        'rgba(255, 99, 132, 0.2)',
                                                        'rgba(255, 99, 132, 0.2)',


                                                    ],
                                                    borderColor: [
                                                        'rgba(132, 255, 99, 1)',
                                                        'rgba(132, 255, 99, 1)',
                                                        'rgba(132, 255, 99, 1)',
                                                        'rgba(132, 255, 99, 1)',
                                                        'rgba(132, 255, 99, 1)',
                                                        'rgba(132, 255, 99, 1)',
                                                        'rgba(132, 255, 99, 1)',
                                                        'rgba(132, 255, 99, 1)',
                                                        'rgba(132, 255, 99, 1)',
                                                        'rgba(132, 255, 99, 1)',
                                                        'rgba(132, 255, 99, 1)',
                                                        'rgba(132, 255, 99, 1)',
     

                                                        
                                                        'rgba(255, 99, 132, 1)',
                                                        'rgba(255, 99, 132, 1)',
                                                        'rgba(255, 99, 132, 1)',
                                                        'rgba(255, 99, 132, 1)',
                                                        'rgba(255, 99, 132, 1)',
                                                        'rgba(255, 99, 132, 1)',
                                                        'rgba(255, 99, 132, 1)',
                                                        'rgba(255, 99, 132, 1)',
                                                        'rgba(255, 99, 132, 1)',
                                                        'rgba(255, 99, 132, 1)',
                                                        'rgba(255, 99, 132, 1)',
                                                        'rgba(255, 99, 132, 1)',
                                                    ],
                                                    borderWidth: 1,
                                                }
                                                ]
                                            },
                                            options: {
                                                scales: {
                                                    yAxes: [{
                                                        ticks: {
                                                            beginAtZero:true
                                                        },
                                                        display: true,
                                                        gridLines: {
                                                            display: true,
                                                            color: 'rgba(255, 255, 255, 0.3)'
                                                        },
                                                    }],
                                                    xAxes: [{
                                                        display: true,
                                                        gridLines: {
                                                            display: true,
                                                            color: 'rgba(255, 255, 255, 0.3)'
                                                        },
                                                    }],
                                                }
                                            }
                                        });


                                    </script>
                                </canvas>
                            </div>



                        </div>
                    </div>
                </body>

            </div>
        </div>
    </div>

</html>