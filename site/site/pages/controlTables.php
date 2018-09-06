<?php
  // this returns a large array of php associative arrays, with each array being a set of entries,  with the field number as the key. 
  // the most recent entry starts at  0, so to get a value from that array you would do echo  "\r\n". $masterArray[0]["120"] . "\r\n"; 
  // with "120" being a field number
  // determines the number of rows to get 
  $input = 1;
  global $data;
  $masterArray = get_data('Weather','onelinedata', $input);
?>

<!-- This code displays the control page -->

<!-- header and icon at top of the page -->
<h2 style="color: white"> <span> <i class="fas fa-user-cog"></i> </span> Controls</h2>


<!-- creates the tabs  -->
<ul class="nav nav-tabs">
  <li class="active"><a href="#controlz" data-toggle="tab" aria-expanded="true">  <span> <i class="fas fa-user-cog"></i></span>  Control </a></li>
  <li class=""><a href="#controlTop" data-toggle="tab" aria-expanded="false">  <span> <i class="fas fa-user-cog"></i> </span> Control Top  </a></li>
  <li class=""><a href="#controlPower" data-toggle="tab" aria-expanded="false">   <span> <i class="fas fa-user-cog"></i></i> </span> Control power </a></li>
</ul>


<!-- contents of the tab goes here -->
<div id="myTabContent" class="tab-content" style=" width: 1000px">


<!--  creates tab 1-->
<!--  make sure id names start with lowercase letter-->
<div class="tab-pane fade active in" id="controlz">
<?php 
  // functions are in index.php file, used to make collpaseable panel, and tables
  // which parse config files, and get values from $masterArray

  makeMainContainerBegin();


  makeCollapsePanelBeginOpen("Fan", "1023");
  makeTable("../config//ControlPage/tabControl/fanTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("ASPIRATED FAN HIGH SPEED", "#");
  makeButton("ASPIRATED FAN HALF SPEED", "#");
  makeButton("ASPIRATED FAN LOW SPEED", "#");
  makeButton("ASPIRATED FAN ON", "#");
  makeButton("ASPIRATED FAN OFF", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Geiger", "1024");
  makeTable("../config//ControlPage/tabControl/geigerTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("GEIGER HIGH VOLTAGE ON", "#");
  makeButton("GEIGER HIGH VOLTAGE OFF", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Snow", "1025");
  makeTable("../config//ControlPage/tabControl/snow.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("IR SNOW DEPTH SENSOR ON", "#");
  makeButton("IR SNOW DEPTH SENSOR OFF", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();

  makeCollapsePanelBegin("Power Supply", "1225");
  makeTable("../config//ControlPage/tabControl/powerSupply.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("POWER SUPPLY BOX FAN ON", "#");
  makeButton("POWER SUPPLY BOX FAN OFF", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Battery", "1026");
  makeTable("../config//ControlPage/tabControl/batteryTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("BATTERY HEATER ON", "#");
  makeButton("BATTERY HEATER OFF", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("DAQ", "1027");
  makeTable("../config//ControlPage/tabControl/DAQTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("RESET TOP DAQ", "#");
  makeButton("RESET MAIN DAQ", "#");
  makeButton("RESET AUX DAQ", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();

  makeMainContainerEnd();
?>
<!-- closes tab 1 -->
</div>


<!-- content of tab 2 goes here -->
<div class="tab-pane fade" id="controlTop" style="width: 1250">
<?php 
  // functions are in index.php file, used to make collpaseable panel, and tables
  // which parse config files, and get values from $masterArray

  makeMainContainerBegin();


  makeCollapsePanelBeginOpen("Voltage", "1028");
  makeTable("../config//ControlPage/tabTop/voltageTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("UVtron HIGH VOLTAGE ON", "#");
  makeButton("UVtron Uvtron HIGH VOLTAGE OFF", "#");
  makeButton("EXECUTE OPT GAIN SETTING", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Hail", "1029");
  makeTable("../config//ControlPage/tabTop/hailTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("HAIL SENSOR HEATER ON", "#");
  makeButton("HAIL SENSOR HEATER OFF", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Motor Coil", "1030");
  makeTable("../config//ControlPage/tabTop/motorTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("MOTOR COIL HEATER ON", "#");
  makeButton("MOTOR COIL HEATER VOLTAGE OFF", "#");
  makeButton("EXECUTE SNOW SWIPE", "#");
  makeButton("SET SNOW SWIPE TO HOME", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Hydreon", "1031");
  makeTable("../config//ControlPage/tabTop/hydreonTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("HYDREON RUN POWER", "#");
  makeButton("HYDREON MICROPOWER", "#");
  makeButton("HYDREON HEATER ON", "#");
  makeButton("HYDREON HEATER OFF", "#");

  makeButton("HYDREON HIGH SENSITIVITY", "#");
  makeButton("HYDREON MID SENSITIVITY VOLTAGE OFF", "#");
  makeButton("HYDREON LOW SENSITIVITY", "#");
  makeButton("HYDREON COUNT RESET ", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("fluxgate", "1032");
  makeTable("../config//ControlPage/tabTop/fluxgateTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("FLUXGATE FGM SENSORS ON", "#");
  makeButton("FLUXGATE FGM SENSORS OFF", "#");
  makeButton("FLUXGATE NULL COILS OFF", "#");
  makeButton("X-AXIS STEP POSTIVE", "#");

  makeButton("X-AXIS STEP NEGATIVE", "#");
  makeButton("X-AXIS COIL SET TO 0 CURRENT", "#");
  makeButton("Y-AXIS STEP POSTIVE ", "#");
  makeButton("Y-AXIS STEP NEGATIVE ", "#");

  makeButton("Y-AXIS COIL SET TO 0 CURRENT", "#");
  makeButton("Z-AXIS STEP POSTIVE", "#");
  makeButton("Z-AXIS STEP NEGATIVE", "#");
  makeButton("Z-AXIS COIL SET TO 0 CURRENT ", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeMainContainerEnd();
?>
<!-- closes tab 2 -->
</div>

<!-- contents of tab 3 go here -->
<div class="tab-pane fade" id="controlPower" style="width: 1250">
<?php 
  // functions are in index.php file, used to make collpaseable panel, and tables
  // which parse config files, and get values from $masterArray

  makeMainContainerBegin();


  makeCollapsePanelBeginOpen("MULTIPLEXER", "10033");
  makeTable("../config//ControlPage/tabPower/multiplexerTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("MULTIPLEXER POWER ON", "#");
  makeButton("MULTIPLEXER POWER OFF", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("LIGHTNING", "1034");
  makeTable("../config//ControlPage/tabPower/lightTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("LIGHTNING SENS POWER ON", "#");
  makeButton("LIGHTNING SENS POWER OFF", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Solar", "1035");
  makeTable("../config//ControlPage/tabPower/solarTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("SOLAR SENSORS POWER ON", "#");
  makeButton("SOLAR SENSORS POWER OFF", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Future", "1036");
  makeTable("../config//ControlPage/tabPower/futureTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("FUTURE SENSORS POWER ON", "#");
  makeButton("FUTURE SENSORS POWER OFF", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Fluxgate ", "10037");
  makeTable("../config//ControlPage/tabPower/fluxTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("FLUXGATE POWER ON", "#");
  makeButton("FLUXGAT  POWER OFF", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("TRIAXIAL", "1038");
  makeTable("../config//ControlPage/tabPower/triaxTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("TRIAX MAGNET. ON", "#");
  makeButton("TRIAX MAGNET. OFF", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("ARBCAM", "1039");
  makeTable("../config//ControlPage/tabPower/arbTable.ini", $masterArray, 0, "Data");
  makeButtonPanelBegin("control");
  makeButton("ARBCAM ON WITH HEATER", "#");
  makeButton("ARBCAM ON NO HEATER", "#");
  makeButton("ARBCAM POWER OFF ", "#");
  makeButtonPanelEnd();
  makeCollapsePanelEnd();




  makeMainContainerEnd();
?>
<!-- closes tab 3 -->
</div>



<!-- closes contents of the tabs -->
</div>



