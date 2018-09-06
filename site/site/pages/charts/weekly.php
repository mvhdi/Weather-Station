
<!doctype html>
<html>
    <head>
        
    <h2>  <span> <i class="far fa-chart-bar"></i> </span> Weekly Charts  </h2>
    <div class="panel panel-default"  >
        <div id="current-conditions" class="panel-collapse collapse in" >
            <div class="panel-body" >

                <body> 



                            <div class="container-fluid"  > 

                                <canvas id="myChart" ></canvas>

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


                                        var ctx = document.getElementById("myChart").getContext('2d');
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
                                                    backgroundColor: 
                                                        'rgba(255, 99, 132, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(255,99,132,1)'
                                                    ,
                                                    borderWidth: 1,
                                                },{
                                                    label: 'Temperature°F Low (Week)',
                                                    fill: false,
                                                    lineTension: 0.2,
                                                    data: dataValuesTwo,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(99, 132, 255, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(99,132,255,1)'
                                                    ,
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

                                <canvas id="myChartTwo" ></canvas>

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


                                        var ctx = document.getElementById("myChartTwo").getContext('2d');
                                        var myChart = new Chart(ctx, {
                                            type: 'line',
                                            
                                            data: {
                                                labels: labelValuesOne,
                                                datasets: [{
                                                    label: 'Humidity% High (Week)',
                                                    fill: false,
                                                    lineTension: 0,
                                                    data: dataValuesOne,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(255, 99, 132, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(255,99,132,1)'
                                                    ,
                                                    borderWidth: 1,
                                                },{
                                                    label: 'Humidity% Low (Week)',
                                                    fill: false,
                                                    lineTension: 0.2,
                                                    data: dataValuesTwo,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(99, 132, 255, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(99,132,255,1)'
                                                    ,
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

                                <canvas id="myChartThree" ></canvas>

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


                                        var ctx = document.getElementById("myChartThree").getContext('2d');
                                        var myChart = new Chart(ctx, {
                                             type: 'line',
                                            
                                            data: {
                                                labels: labelValuesOne,
                                                datasets: [{
                                                    label: 'Barometric Pressure (hPa) High (Week)',
                                                    fill: false,
                                                    lineTension: 0,
                                                    data: dataValuesOne,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(255, 99, 132, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(255,99,132,1)'
                                                    ,
                                                    borderWidth: 1,
                                                },{
                                                    label: 'Barometric Pressure (hPa) Low (Week)',
                                                    fill: false,
                                                    lineTension: 0.2,
                                                    data: dataValuesTwo,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(99, 132, 255, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(99,132,255,1)'
                                                    ,
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
                            </div>
                            <div class="container-fluid"  > 

                                <canvas id="myChart4" ></canvas>

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


                                        var ctx = document.getElementById("myChart4").getContext('2d');
                                        var myChart = new Chart(ctx, {
                                            type: 'line',
                                            
                                            data: {
                                                labels: labelValuesOne,
                                                datasets: [{
                                                    label: 'WindChill°F High (Week)',
                                                    fill: false,
                                                    lineTension: 0,
                                                    data: dataValuesOne,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(255, 99, 132, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(255,99,132,1)'
                                                    ,
                                                    borderWidth: 1,
                                                },{
                                                    label: 'WindChill°F Low (Week)',
                                                    fill: false,
                                                    lineTension: 0.2,
                                                    data: dataValuesTwo,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(99, 132, 255, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(99,132,255,1)'
                                                    ,
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

                            </div>

                            <div class="container-fluid"  > 

                                <canvas id="myChart5" ></canvas>

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


                                        var ctx = document.getElementById("myChart5").getContext('2d');
                                        var myChart = new Chart(ctx, {
                                            type: 'line',
                                            
                                            data: {
                                                labels: labelValuesOne,
                                                datasets: [{
                                                    label: 'Heat Index°F High (Week)',
                                                    fill: false,
                                                    lineTension: 0,
                                                    data: dataValuesOne,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(255, 99, 132, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(255,99,132,1)'
                                                    ,
                                                    borderWidth: 1,
                                                },{
                                                    label: 'Heat Index°F Low (Week)',
                                                    fill: false,
                                                    lineTension: 0.2,
                                                    data: dataValuesTwo,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(99, 132, 255, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(99,132,255,1)'
                                                    ,
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

                            </div>
                            <div class="container-fluid"  > 

                                <canvas id="myChart6" ></canvas>

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


                                        var ctx = document.getElementById("myChart6").getContext('2d');
                                        var myChart = new Chart(ctx, {
                                            type: 'line',
                                            
                                            data: {
                                                labels: labelValuesOne,
                                                datasets: [{
                                                    label: 'Rain Fall (in) High (Week)',
                                                    fill: false,
                                                    lineTension: 0,
                                                    data: dataValuesOne,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(255, 99, 132, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(255,99,132,1)'
                                                    ,
                                                    borderWidth: 1,
                                                },{
                                                    label: 'Rain Fall (in) Low (Week)',
                                                    fill: false,
                                                    lineTension: 0.2,
                                                    data: dataValuesTwo,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(99, 132, 255, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(99,132,255,1)'
                                                    ,
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

                            </div>
                            <div class="container-fluid"  > 

                                <canvas id="myChart7" ></canvas>

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


                                        var ctx = document.getElementById("myChart7").getContext('2d');
                                        var myChart = new Chart(ctx, {
                                            type: 'line',
                                            
                                            data: {
                                                labels: labelValuesOne,
                                                datasets: [{
                                                    label: 'Wind Speed (mph) High (Week)',
                                                    fill: false,
                                                    lineTension: 0,
                                                    data: dataValuesOne,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(255, 99, 132, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(255,99,132,1)'
                                                    ,
                                                    borderWidth: 1,
                                                },{
                                                    label: 'Wind Speed (mph) Low (Week)',
                                                    fill: false,
                                                    lineTension: 0.2,
                                                    data: dataValuesTwo,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(99, 132, 255, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(99,132,255,1)'
                                                    ,
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

                            </div>
                            <div class="container-fluid"  > 

                                <canvas id="myChart7" ></canvas>

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


                                        var ctx = document.getElementById("myChart7").getContext('2d');
                                        var myChart = new Chart(ctx, {
                                            type: 'line',
                                            
                                            data: {
                                                labels: labelValuesOne,
                                                datasets: [{
                                                    label: 'Dew Point°F High (Week)',
                                                    fill: false,
                                                    lineTension: 0,
                                                    data: dataValuesOne,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(255, 99, 132, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(255,99,132,1)'
                                                    ,
                                                    borderWidth: 1,
                                                },{
                                                    label: 'Dew Point°F Low (Week)',
                                                    fill: false,
                                                    lineTension: 0.2,
                                                    data: dataValuesTwo,
                                                    pointHoverBorderWidth: 25,
                                                    pointHoverBorderColor: 'rgba(0, 0, 0, 0.50)',
                                                    backgroundColor: 
                                                        'rgba(99, 132, 255, 0.2)'
                                                    ,
                                                    borderColor: 
                                                    'rgba(99,132,255,1)'
                                                    ,
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