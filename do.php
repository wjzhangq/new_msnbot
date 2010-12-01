<?php
date_default_timezone_set('Asia/Chongqing');
class sClient{
	var $fp;
	var $stop = 0;
	function __construct($host, $port){
		$fp = fsockopen($host, $port, $errno, $errstr, 30);
		if (!$fp){
			throw new Exception($errstr);
		}
		$this->fp = $fp;
	}
	
	function isWork(){
		return $this->stop == 0;
	}
	
	function get(){
		$str = fread($this->fp, 10240);
		if ($str === false){
			$this->stop = 1;
		}
		
		return $str;
	}
	
	function send($msg){
		$ret = fwrite($this->fp, $msg);
		if ($ret === false){
			$this->stop = 1;
		}
	}
}

$n = new sClient('127.0.0.1', 2001);
while($n->isWork()){
	$msg = $n->get();
	var_dump($msg);
	$n->send(date('H:i:s'));
}


?>