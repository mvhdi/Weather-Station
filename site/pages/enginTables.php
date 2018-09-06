<?php
  // this returns a large array of php associative arrays, with each array being a set of entries,  with the field number as the key. 
  // the most recent entry starts at  0, so to get a value from that array you would do echo  "\r\n". $masterArray[0]["120"] . "\r\n"; 
  // with "120" being a field number
  // determines the number of rows to get 
  $input = 1;
  global $data;
  $masterArray = get_data('Weather','onelinedata', $input);
?>

<!-- This code displays the engineering page -->

<!-- header and icon at top of the page -->
<h2 style="color: white"> <span> <i class="fas fa-bolt"></i> </span> Engineering </h2>

<!-- creates the tabs  -->
<ul class="nav nav-tabs">
  <li class="active"><a href="#engineeringPower" data-toggle="tab" aria-expanded="true">  <span> <i class="fas fa-bolt"></i></span>  Engineering Power </a></li>
  <li class=""><a href="#engineeringA" data-toggle="tab" aria-expanded="false">  <span> <i class="fas fa-bolt"></i> </span>  Engineering A  </a></li>
  <li class=""><a href="#engineeringB" data-toggle="tab" aria-expanded="false">   <span> <i class="fas fa-bolt"></i></i> </span>  Engineering B </a></li>
</ul>


<!-- contents of the tab goes here -->
<div id="myTabContent" class="tab-content">


<!--  creates tab 1-->
<!-- make sure id names start with lowercase letters-->
<div class="tab-pane fade active in" id="engineeringPower">
<?php 
  // functions are in index.php file, used to make collpaseable panel, and tables
  // which parse config files, and get values from $masterArray

  makeMainContainerBegin();


  makeCollapsePanelBeginOpen("Solar Panel", "1008");
  makeTable("../config//enginePage/tabPower/solarPanelTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("DAQ System", "1009");
  makeTable("../config//enginePage/tabPower/DAQTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Battery", "1010");
  makeTable("../config//enginePage/tabPower/batteryTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Tower", "1011");
  makeTable("../config//enginePage/tabPower/towerTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeMainContainerEnd();
?>

<!-- closes tab 1 -->
</div>


<!-- content of tab 2 goes here -->
<div class="tab-pane fade" id="engineeringA" >
<?php 
  // functions are in index.php file, used to make collpaseable panel, and tables
  // which parse config files, and get values from $masterArray

  makeMainContainerBegin();


  makeCollapsePanelBeginOpen("Mutiplexer", "1012");
  makeTable("../config//enginePage/tabA/multTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Hydreon", "1013");
  makeTable("../config//enginePage/tabA/hydTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Sky Sensor", "1014");
  makeTable("../config//enginePage/tabA/skyTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Sway Sensor", "1015");
  makeTable("../config//enginePage/tabA/swayTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Lightning Sensor", "1016");
  makeTable("../config//enginePage/tabA/lightTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Solar", "1017");
  makeTable("../config//enginePage/tabA/solarTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Arbcam", "1018");
  makeTable("../config//enginePage/tabA/arbTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeMainContainerEnd();
?>
<!-- closes tab 2 -->
</div>

<!-- contents of tab 3 go here -->
<div class="tab-pane fade" id="engineeringB" >
<?php 
  // functions are in index.php file, used to make collpaseable panel, and tables
  // which parse config files, and get values from $masterArray

  makeMainContainerBegin();


  makeCollapsePanelBeginOpen("Top DAQ", "10019");
  makeTable("../config//enginePage/tabB/TopDAQ.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Geiger", "1020");
  makeTable("../config//enginePage/tabB/geigerTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Temperature", "1021");
  makeTable("../config//enginePage/tabB/tempTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Soil - Misc sensors", "1022");
  makeTable("../config//enginePage/tabB/soil-miscTable.ini", $masterArray, 0, "Data");
  makeCollapsePanelEnd();


  makeMainContainerEnd();
?>
<!-- closes tab 3 -->
</div>



<!-- closes contents of the tabs -->
</div>



