<?php
	session_start();
	set_include_path('/Users/weatherfolk/Sites/backend/phpseclib1.0.9');
	include('Net/SSH2.php');
	if(isset($_SESSION['adm']) && isset($_POST['page']) && isset($_POST['col']) && isset($_POST['name'])) {
		$conf = parse_ini_file("../config/" . $_POST['page'] . ".ini", true);
		$host_info = parse_ini_file("../config/host.ini", true);
		$code = $conf['button.' . $_POST['col'] . '.' . $_POST['name']]['msg'];

		// send $code there
		$code = $code . "\tDASH\n";
		// $connection = ssh2_connect($host_info['server']['host']);
		// if (!$connection) {
		// 	http_response_code(401);
		// }
		// ssh2_auth_password($connection, $host_info['server']['user'], $host_info['server']['pwd']) or die("Unable to authenticate");
		// ssh2_exec($connection, );
		$ssh = new Net_SSH2($host_info['server']['host']);
		if (!$ssh->login($host_info['server']['user'], $host_info['server']['pwd'])) {
		    http_response_code(500);
		}
		$ssh->exec("echo '" . $code . "' >> " . $host_info['server']['commandpath']);
    } else {
    	http_response_code(401);
    }
?>