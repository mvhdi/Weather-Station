<?php
  // this returns a large array of php associative arrays, with each array being a set of entries,  with the field number as the key. 
  // the most recent entry starts at  0, so to get a value from that array you would do echo  "\r\n". $masterArray[0]["120"] . "\r\n"; 
  // with "120" being a field number
  // determines the number of rows to get 
  $input = 1;
  global $data;
  $masterArray = get_data('Weather','onelinedata', $input);
?>


<h2 style="color: white"  > <span> <i class="fab fa-envira" ></i>  </span> Soil</h2>

<?php 
  // functions are in the index.php file, they are used to make the main container,collpaseable panels, and tables
  // which parse config files, and get db values from $masterArray

  


  makeCollapsePanelBeginOpen("Air Temperature", "1000");
  makeTable("../config//soilPage/airAbove1.ini", $masterArray, 0, "Above Ground");
  makeTable("../config//soilPage/airAbove2.ini", $masterArray, 0, "Above Ground");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Soil Temperature", "1001");
  makeTable("../config//soilPage/soilBelow1.ini", $masterArray, 0, "Below Ground");
  makeTable("../config//soilPage/soilBelow2.ini", $masterArray, 0, "Below Ground");
  makeTable("../config//soilPage/soilBelow3.ini", $masterArray, 0, "Below Ground");
  makeCollapsePanelEnd();


  makeCollapsePanelBegin("Soil Moisture", "1002");
  makeTable("../config//soilPage/soilMoist.ini", $masterArray, 0, "Below Ground");
  makeCollapsePanelEnd();


  
?>

