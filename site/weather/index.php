<?php 
session_start();
?>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="icon" href="./favicon.ico">
        <title>Carleton Weather Station</title>


        <link href="./lib/bootswatch-3.3.2/bootstrap-slate.min.css" rel="stylesheet">
       
        
        <script src="./lib/jquery-1.11.1/jquery.min.js"></script>
        <script src="./lib/bootstrap-3.3.7/js/bootstrap.min.js"></script>
        


        <script src="./lib/jquery-1.11.1/chart.js"></script>
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.1.0/css/all.css" integrity="sha384-lKuwvrZot6UHsBSfcMvOkWwlCMgc0TaWr+30HWe3a4ltaBwTZhyTEggF5tJv8tbt" crossorigin="anonymous">

        <!-- Weather Warning widget (only displays when warning exists) to test is out append /?testWarning=1 to the end of the url-->
        <script src="https://cdnres.willyweather.com/widget/warning/loadView.html?id=93554" type="application/javascript"></script>
        
    </head>

    <body>
        <h2> &nbsp; </h2>
        <div class="navbar navbar-default navbar-fixed-top" role="navigation">
            <div class="container">
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle collapsed " data-toggle="collapse" data-target=".navbar-collapse">  
                        <span class="sr-only"> Toggle navigation </span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>


                    <a class="navbar-brand"  style="color: white" href="index.php"> <span> <img src="wi-day-rain-mix.svg" width="25" height="25" > </span> Carleton Weather </a>


                </div>
                <div class="collapse navbar-collapse" >
                    <ul class="nav navbar-nav" id="myNav">
                        
                        
                        <li> <a class='btn nav-btn' style="color: white" data-page='Now'>&nbsp;&nbsp; <span> <i class="far fa-clock"></i> </span> Now </a></li>
                        <li> <a class='btn nav-btn' style="color: white" data-page='Forecasts' >&nbsp;&nbsp; <span> <i class="fas fa-cloud"></i> </span> Forecasts </a></li>
                        <li> <a class='btn nav-btn' style="color: white" data-page='soilTables'> &nbsp;&nbsp; <span> <i class="fab fa-envira"></i> </span> Soil </a></li>
                        <li> <a class='btn nav-btn' style="color: white" data-page='sensorTables'> &nbsp;&nbsp; <span> <i class="far fa-eye"></i> </span> Sensors </a></li>
                        <li> <a class='btn nav-btn' style="color: white" data-page='enginTables'> &nbsp;&nbsp; <span> <i class="fas fa-bolt"></i></i> </span> Engineering </a></li>
                        <li> <a class='btn nav-btn' style="color: white" data-page='controlTables'> &nbsp;&nbsp; <span> <i class="fas fa-user-cog"></i> </span> Controls</a></li>

                      <!--   <li> <a class='btn nav-btn' style="color: white" data-page='charts'> &nbsp;&nbsp; <span> <i class="far fa-chart-bar"></i>  </span> Charts</a></li> -->
                        <!-- class active makes the page appear first, adjust it in the script if you change it. -->
                        <li class="active"> <a class='btn nav-btn' style="color: white" data-page='All'>&nbsp;&nbsp; <span> <i class="fas fa-table"></i> </span> All Data </a></li>
                    
                        
                        
                    </ul>
                </div>
            </div>
        </div>



        <script type="text/javascript">            
            $('.nav-btn').on('click', function(event) {
                event.preventDefault();
                $("#" + $(event.target).data('page')).show().siblings().hide();
                ($(event.target).parent()).addClass('active').siblings().removeClass('active');
                window.location.hash = $(event.target).data('page');
                window.scrollTo(0, 0);
            });

        </script>

        <h5> &nbsp; </h5>

        <div class="container" style=" max-width: 80%; margin:0 auto">
            <?php 

                // new website function
                // function version of the code above, lets us use any database.
                // connects to the given database and runs the given sql command, and returns the output in an array
                // of maps, which have the filedname as the key, and the value as the value. 
                function get_data($database, $tablename, $numberOfEntries) {

                    // info for connecting to the database
                    $db = $database;
                    $dbconf = parse_ini_file("../config/db.ini", true);
                    $host = $dbconf['db']['host'];
                    $usr = $dbconf['db']['usr'];
                    $pwd = $dbconf['db']['pwd'];
                    // connect to the database...
                    $conn = new mysqli($host, $usr, $pwd , $db);
                    if ($conn->connect_error) {
                        echo "fail";
                    }
                    // make the query with given command
                    $sql = "SELECT * FROM " . $tablename . " order by `1` desc limit ". $numberOfEntries ." ;";
                    // temp array to store values from database 
                    $dataArr = array();
                    // array of maps that will be returned
                    $masterArray = array();
                    // holds results from the query
                    $result = mysqli_query($conn, $sql);

                    // iterates through the results and puts values for each input in a map,
                    // and then pushes that map into a larger array of maps
                    while($row = mysqli_fetch_assoc($result)) {
                        //map (assotive array) to store fieldname value pairs 
                        $dataMap = array();
                        foreach($row as $fieldname => $value){
                            array_push($dataArr, $value);
                            $dataMap[$fieldname] = $value;   
                        }
                        //adds the map of fields and values for an input to the larger array
                        array_push($masterArray, $dataMap); 
                    }
                    // ...closes the database connection
                    mysqli_close($conn);
                    //recommeded practice of clearing
                    mysqli_free_result($result);

                    return $masterArray;
                }

                // new set of fuctions, used by new version of the site
                // used to generate tables

                // converter
                function convertAndPrint( $label, $value, $units) {

                    $conv = 0;
                    $altUnit = "";
                    $orgUnit = "";
                    switch ($units) {
                        case "F-C":
                            $conv = ($value - 32) * 5.0 / 9.0;
                            $conv = round($conv, 1);
                            $value = round($value, 1);
                            $altUnit = "°C";
                            $orgUnit = "°F";
                            break;
                        case "inch-cm":
                            $conv = $value * 2.54;
                            $conv = round($conv, 1);
                            $value = round($value, 1);
                            $altUnit = "cm";
                            $orgUnit = "inch";
                            break;
                        case "mph-m/s":
                            $conv = $value * 0.447;
                            $conv = round($conv, 1);
                            $value = round($value, 1);
                            $altUnit = "m/s";
                            $orgUnit = "mph";
                            break;
                        case "inch-hPa":
                            $conv = $value * 3386.39;
                            $conv = round($conv, 1);
                            $value = round($value, 1);
                            $altUnit = "hPa";
                            $orgUnit = "inch";
                            break;
                        default:
                            $conv = ' ';
                            $altUnit = ' ';
                            $orgUnit = $units;
                            $value = $value;
                            break;
                    }
                    
                    echo "<td> <h4>". $label . "</h4> </td>";
                    echo "<td> <h4>". $value . " ". $orgUnit . "</h4> </td>";
                    echo "<td> <h4>". $conv . " ". $altUnit . "</h4> </td>";
                    
                        
                }
                // makes a panel that it initally closed 
                function makeCollapsePanelBegin($title, $num){
                  echo '<div class="table-responsive" >';
                  echo '<div class="panel-group" >';
                  echo '<div class="panel panel-default">';
                  echo '<div class="panel-heading">';
                  echo '<h4 class="panel-title">';
                  echo '<a data-toggle="collapse" href="#collapse'.$num.'" style="color: white" >'.$title.'</a>';
                  echo '</h4>';
                  echo '</div>';
                  echo '<div id="collapse'.$num.'" class="panel-collapse collapse  ">';
                  echo '<div class="panel-body" style="width: 990px; border-color:  #272B30" >';
                }

                // the only diffeence is this creates a panel that is initally open
                function makeCollapsePanelBeginOpen($title, $num){
                  echo '<div class="table-responsive" >';
                  echo '<div class="panel-group" >';
                  echo '<div class="panel panel-default">';
                  echo '<div class="panel-heading sytle="border-color:  #272B30">';
                  echo '<h4 class="panel-title">';
                  echo '<a data-toggle="collapse" href="#collapse'.$num.'" style="color: white" >'.$title.'</a>';
                  echo '</h4>';
                  echo '</div>';
                  echo '<div id="collapse'.$num.'" class="panel-collapse collapse in ">';
                  echo '<div class="panel-body" style="width: 990px; border-color:  #272B30" >';
                }
                function makeCollapsePanelEnd(){
                  echo '</div>';
                  echo '</div>';
                  echo '</div>';
                  echo '</div>';
                  echo '</div>';

                }

                function generateTableBegin() {
                echo '<div class=" table-responsive ">';
                echo '<table class="table table-striped table-condensed  table-hover ">';
                echo '<tbody style="color: white; border-color:  #272B30 ">';
                }

                function generateTableEnd(){
                  echo '</tbody>';
                  echo '</table>';
                  echo '</div >';

                }

                function generateTablePanelBegin($title){
                  echo '<div class="table-responsive" >';
                  echo '<div class="panel panel-primary" style="height:400x; ">';
                  echo '<div class="panel-heading" style="text-align: center">';
                  echo '<h4 class="panel-title" style="color: white" > '.$title.' </h4>';
                  echo '</div>';
                  echo '<div class="panel-body" style="color: white; border-color:  #272B30 ">';

                }

                function generateTablePanelEnd(){
                  echo '</div>';
                  echo '</div>';
                  echo '</div>';

                }

				// check out https://getbootstrap.com/docs/3.3/examples/grid/ 
                function generateTableGridBegin(){
                  echo '<div class="col-xs-6 .col-sm-6 .col-md-6" >';
                }

                function generateTableGridEnd(){
                  echo '</div>';

                }

                function generateRowBegin(){
                  echo '<tr>';
                }
                function generateRowEnd(){
                  echo '</tr>';
                }

                function makeMainContainerBegin(){
                  echo '<div class="panel panel-default">';
                  echo '<div class="panel-body">';

                }

                function makeMainContainerEnd(){
                  echo '</div>';
                  echo '</div>';

                }
                function getLastUpdateTime($array){
                  $hour = round($array[0]["5"], 1);
                  $min = round($array[0]["6"], 1);
                  $sec = round($array[0]["7"], 1);

                  $month = round($array[0]["3"], 1);
                  $day = round($array[0]["4"], 1);
                  $year = round($array[0]["2"], 1);


                  echo '<tr>';
                  echo "<td> <h4>". "Updated On:" . "</h4> </td>";
                  echo '<td>';
                  echo '<h4>';
                  echo $hour . ":". $min. ":". $sec;
                  echo '</h4>';
                  echo '</td>';
                  echo "<td> <h4>". $month. "/". $day. "/". $year . "</h4> </td>";
                  echo '</tr>';
                }

                function makeTable($tableFile, $daArray, $dbEntry, $label){

                  generateTableGridBegin();
                  generateTablePanelBegin($label);
                  generateTableBegin();

                  $conf = parse_ini_file($tableFile, true);
                  // display the data
                  foreach ($conf as $fullname => $info) {
                      // preprocess -> $name
                      if (substr($fullname, 0, 7) !== "fields.") {
                          continue;
                      }
                      $name = substr($fullname, 7);


                      $label = $name;
                      $fn = $info["fn"];
                      $unit = $info["unit"];


                      generateRowBegin();
                      convertAndPrint($label, $daArray[$dbEntry][$fn], $unit );
                      generateRowEnd(); 

                  }

                  generateTableEnd();
                  generateTablePanelEnd();
                  generateTableGridEnd(); 


                }
                function makeButtonPanelBegin($label){
                  generateTableGridBegin();
                  generateTablePanelBegin($label);
                }

                function makeButtonPanelEnd(){
                  generateTablePanelEnd();
                  generateTableGridEnd();

                }

                // to get button to work delete disabled in the class in this fuction
                function makeButton($label, $link){
                  echo '<a href='.$link.' class="btn btn-default disabled btn-lg btn-block" style="white-space: normal !important; word-wrap: break-word;" >'.$label.'</a>';
                }


            ?>


            <div class="nav-pages" id="All">
                <?php include('../pages/All.php'); ?>
            </div>

          <div class="nav-pages" id="Forecasts">
                <?php include('../pages/forecast.php'); ?>
            </div> 

            <div class="nav-pages" id="Now">
                <?php include('../pages/Now.php'); ?>
            </div>
            <div class="nav-pages" id="soilTables">
                <?php include('../pages/soilTables.php'); ?>
            </div>
            <div class="nav-pages" id="sensorTables">
                <?php include('../pages/sensorTables.php'); ?>
            </div>
            <div class="nav-pages" id="controlTables">
                <?php include('../pages/controlTables.php'); ?>
            </div>
            <div class="nav-pages" id="enginTables">
                <?php include('../pages/enginTables.php'); ?>
            </div>
<!--             <div class="nav-pages" id="charts">
                <?php // include('../pages/charts/weekly.php'); ?>
            </div> -->

        <!-- controls what page is shown first -->
        <script type="text/javascript">
            if (window.location.hash != "") {
                var page = window.location.hash;
                $(page).show().siblings().hide();
                var tab = $("#myNav a[data-page='" + page.substring(1) + "']");
                (tab.parent()).addClass('active').siblings().removeClass('active');
            } else {
                $("#All").show().siblings().hide();
            }
        </script>
    </div>

        <h2> &nbsp; </h2>
        <div class="footer">
            <div class="container" >
                <p class="text-muted">Copyright &#169; 2017-<?php date_default_timezone_set("America/Chicago"); echo date("Y");?> <a href='https://www.carleton.edu'>Carleton College</a></p>
            </div>
        </div>
       

</html>