<?php
  $input = 1;
  $rawDataArray = get_data('Weather','rawdata', $input);
  $convertedDataArray = get_data('Weather','converteddata', $input);
?>

<?php
function makeFieldDataTable($tableFile, $rawArray, $convertedArray, $dbEntry, $label){
  //generateTableGridBegin();
  generateTablePanelBegin($label);
  generateTableBegin();
  	generateRowBegin();
	echo "<td> <h5> Converted Field Name </h5> </td>";
	echo "<td> <h5> Raw Field Name </h5> </td>";
	echo "<td> <h5> Raw Value </h5> </td>";
	echo "<td> <h5> Coverted Value </h5> </td>";
	echo "<td> <h5>Raw Field Number </h5> </td>";
	echo "<td> <h5>Converted Field Number </h5> </td>";

	generateRowEnd(); 
  $conf = parse_ini_file($tableFile, true);
  // display the data
  foreach ($conf as $fullname => $info) {
      // preprocesvs -> $name
      if (substr($fullname, 0, 7) !== "fields.") {
          continue;
      }
      $name = substr($fullname, 7);
      $conFNAME = $info["conName"];
      $rawFNAME = $name; 
      $rawFN = $info["rawFN"];
      $convFN = $info["convFN"];
      generateRowBegin();
      printFieldData($conFNAME, $rawFNAME, $rawArray[$dbEntry][$rawFN], $convertedArray[$dbEntry][$convFN], $rawFN, $convFN );
      generateRowEnd(); 
  }
  generateTableEnd();
  generateTablePanelEnd();
  //generateTableGridEnd(); 
}
function printFieldData( $conFNAME, $rawFNAME, $raw, $converted,$rawFN, $convFN) {
    echo "<td> <h5>". $conFNAME . "</h5> </td>";
    echo "<td> <h5>". $rawFNAME . "</h5> </td>";
    echo "<td> <h5>". $raw . "</h5> </td>";
    echo "<td> <h5>". $converted . "</h5> </td>"; 
    echo "<td> <h5>". $rawFN . "</h5> </td>";
    echo "<td> <h5>". $convFN . "</h5> </td>";
      
}
?>
<!-- This code displays the engineering page -->

<!-- header and icon at top of the page -->
<h2 style="color: white"> <span> <i class="fas fa-table"></i> </span> All Data </h2>

<!-- creates the tabs  -->
<ul class="nav nav-tabs">
  <li class="active"><a href="#timedata" data-toggle="tab" aria-expanded="true">  <span> <i class="fas fa-table"></i> </span>  Time </a></li>
  <li class=""><a href="#topdata" data-toggle="tab" aria-expanded="false">  <span><i class="fas fa-table"></i> </span> Top   </a></li>
  <li class=""><a href="#bottomdata" data-toggle="tab" aria-expanded="false">   <span> <i class="fas fa-table"></i> </i> </span>  Bottom  </a></li>
   <li class=""><a href="#soildata" data-toggle="tab" aria-expanded="false">   <span> <i class="fas fa-table"></i> </i> </span>  Soil  </a></li>
</ul>


<!-- contents of the tab goes here -->
<div id="myTabContent" class="tab-content">


<!--  creates tab 1-->
<!-- make sure id names start with lowercase letters-->
<div class="tab-pane fade active in" id="timedata">
<?php 
  // functions are in index.php file, used to make collpaseable panel, and tables
  // which parse config files, and get values from $masterArray

  makeMainContainerBegin();
  makeFieldDataTable("../config//allData/timeData.ini",  $rawDataArray, $convertedDataArray, 0, "Time Data");
  makeMainContainerEnd();
?>

<!-- closes tab 1 -->
</div>


<!-- content of tab 2 goes here -->
<div class="tab-pane fade" id="topdata" >
<?php 
  // functions are in index.php file, used to make collpaseable panel, and tables
  // which parse config files, and get values from $masterArray

  makeMainContainerBegin();
  makeFieldDataTable("../config//allData/topSec/adjustedTop.ini",  $rawDataArray, $convertedDataArray, 0, "Top Data");
  makeMainContainerEnd();
?>
<!-- closes tab 2 -->
</div>

<!-- contents of tab 3 go here -->
<div class="tab-pane fade" id="bottomdata" >
<?php 
  // functions are in index.php file, used to make collpaseable panel, and tables
  // which parse config files, and get values from $masterArray

  makeMainContainerBegin();

  makeFieldDataTable("../config//allData/bottomSec/adjustedBottom.ini",  $rawDataArray, $convertedDataArray, 0, "Bottom Data");
  makeMainContainerEnd();
?>
<!-- closes tab 3 -->
</div>

<!-- contents of tab 4 go here -->
<div class="tab-pane fade" id="soildata" >
<?php 
  // functions are in index.php file, used to make collpaseable panel, and tables
  // which parse config files, and get values from $masterArray

  makeMainContainerBegin();

  makeFieldDataTable("../config//allData/soilSec/adjustedSoilSec.ini",  $rawDataArray, $convertedDataArray, 0, "Soil
  Data");

  makeMainContainerEnd();
?>
<!-- closes tab 4 -->
</div>


<!-- closes contents of the tabs -->
</div>
