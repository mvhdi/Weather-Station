<?php
	session_start();
	if(isset($_POST['pwd'])) {
		$conf = parse_ini_file("../config/adm.ini", true);
		if ($_POST['pwd'] === $conf['adm']['pwd']) {
			if (!isset($_SESSION['adm'])) {
				// login
				$_SESSION['adm'] = true;
			} else {
				// logout
				unset($_SESSION['adm']);
			}
			session_write_close();
			http_response_code(200);
        } else {
        	http_response_code(401);
        }
    }
?>