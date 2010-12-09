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
		
		$data = json_decode($str);
		if ($data){
			$tmp = (array) $data;
			if (isset($tmp['data'][1])){
				$tmp['data'][1] = (array) $tmp['data'][1];
			}
			$data = $tmp;
			if (isset($data['data'][1]['Content-Type']) && $data['data'][1]['Content-Type'] == 'text/x-msmsgscontrol'){
				$data['type'] = 'control';
			}else{
				if (isset($data['data'][2])){
					$data['msg'] = trim($data['data'][2][0]);
				}
			}
		}else{
			$data = array('type'=>'error', 'data'=>'json decode error:' . $str);
		}

		
		return $data;
	}
	
	function send($msg){
		$ret = fwrite($this->fp, $msg);
		if ($ret === false){
			$this->stop = 1;
		}
	}
}

$n = new sClient('127.0.0.1', 9876);
while($n->isWork()){
	$msg = $n->get();
	if ($msg['type'] == 'msg'){
		if ($msg['msg'] == ''){
			print_r($msg);
		}else{
			var_dump($msg['msg']);
			$n->send('abc' . $msg['msg']);
		}
	}else{
		//don some thing
	}
	
}


?>