<?php
  // this returns a large array of php associative arrays, with each array being a set of entries,  with the field number as the key. 
  // the most recent entry starts at  0, so to get a value from that array you would do echo  "\r\n". $masterArray[0]["120"] . "\r\n"; 
  // with "120" being a field number
  // determines the number of rows to get 
  $input = 1;
  global $data;
  $masterArray = get_data('Weather','converteddata', $input);
?>

<div class="panel panel-default" style="background-color: #272B30; border-color:  #272B30"; >
 
<div class="panel-heading" style="background-color: #272B30; border-color:  #272B30; color: white"><h2 > <span> <i class="far fa-clock"></i></span> Weather Now</h2></div>
  <div class="panel-body" style="margin-left:0px; margin-top: 0%">

<div class="col-xs-6 .col-sm-6 .col-md-6" >
  <div class="panel panel-primary " style="height:400x;  ">
    <div class="panel-heading" style="text-align: center">
      <h4 class="panel-title" style="color: white"> CURRENT </h4>
    </div>
    <div class="panel-body" style="color: white;  word-break:break-all">
      <table class="table table-striped table-condensed table-responsive  table-hover " >
        <tbody style="color: white">
            <?php 
              getLastUpdateTime($masterArray);
            ?>
          <tr>
            <?php 
                convertAndPrint("Temperature", $masterArray[0][120], "F-C" );
             ?>

          </tr>
          <tr>
            <?php 
                convertAndPrint("Humidity", $masterArray[0][123], "%" );
             ?>
        </tr>
        <tr>
            <?php 
                convertAndPrint("Pressure", $masterArray[0][134], "inch-hPa" );
             ?>
        </tr>
 
        </tbody>
    </table> 
  </div>
  </div>
</div>


<?php
  makeTable("../config//nowPage/precepTable.ini", $masterArray, 0, "Precipitation");
  makeTable("../config//nowPage/windTable.ini", $masterArray, 0, "Wind");
  makeTable("../config//nowPage/tempTable.ini", $masterArray, 0, "Temperature");
  makeTable("../config//nowPage/solarTable.ini", $masterArray, 0, "Solar");
  makeTable("../config//nowPage/skyTable.ini", $masterArray, 0, "Sky");
?>



</div>
</div>



