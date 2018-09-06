<?php
  // this returns a large array of php associative arrays, with each array being a set of entries,  with the field number as the key. 
  // the most recent entry starts at  0, so to get a value from that array you would do echo  "\r\n". $masterArray[0]["120"] . "\r\n"; 
  // with "120" being a field number
  // determines the number of rows to get 
  $input = 1;
  global $data;
  $masterArray = get_data('Weather','onelinedata', $input);
?>


<h2 style="color: white" > <span> <i class="far fa-eye"></i>  </span> Sensors</h2>

<?php 
  // functions are in index.php file, used to make collpaseable panel, and tables
  // which parse config files, and get values from $masterArray




  makeCollapsePanelBeginOpen("Misc Sensors", "1003");
  makeTable("../config//sensorPage/pressureTable.ini", $masterArray, 0, "Barometric Pressure");
  makeTable("../config//sensorPage/humidTable.ini", $masterArray, 0, "Humidity");
  makeTable("../config//sensorPage/leafTable.ini", $masterArray, 0, "Leaf Sensor");
  makeTable("../config//sensorPage/geiger.ini", $masterArray, 0, "Geiger Counter");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Precipitation Sensors", "1004");
  makeTable("../config//sensorPage/snowTable.ini", $masterArray, 0, "Snow Depth");
  makeTable("../config//sensorPage/frostTable.ini", $masterArray, 0, "Frost");
  makeTable("../config//sensorPage/rainTable.ini", $masterArray, 0, "Rain Sensor");
  makeTable("../config//sensorPage/hail.ini", $masterArray, 0, "Hail Sensor");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Temperature Sensors", "1005");
  makeTable("../config//sensorPage/head1Table.ini", $masterArray, 0, "Head Sensor");
  makeTable("../config//sensorPage/head2Table.ini", $masterArray, 0, "Head Sensor");
  makeTable("../config//sensorPage/tempTable.ini", $masterArray, 0, "Temperature Sensor");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Wind Sensors", "1006");
  makeTable("../config//sensorPage/windTable.ini", $masterArray, 0, "Wind Speed Sensor");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Lighting Sensors", "1007");
  makeTable("../config//sensorPage/lightningTable.ini", $masterArray, 0, "Lightning Sensors");
  makeCollapsePanelEnd();


  
?>


