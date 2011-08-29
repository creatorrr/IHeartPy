/*
** Initialize Objects
*/

var _LOL_MODE=0;


function trim(str){
		return str.replace(/^\s*/,"").replace(/\s*$/,"");
		}


	var shellClient = {}
		shellClient.DONE_STATE = 4;

		shellClient.getXmlHttpRequest = function() {
				if (window.XMLHttpRequest) {
					return new XMLHttpRequest();
					}
				else if (window.ActiveXObject) {
					try {
						return new ActiveXObject('Msxml2.XMLHTTP');
						}
					catch(e) {
						return new ActiveXObject('Microsoft.XMLHTTP');
						}
					}
				return null;
				};

		shellClient.fetchResult = function(result) {
				result='\n>>> '+result;
				document.getElementById('display').innerHTML += result;
				document.getElementById('prompt').innerHTML = '';
				return true;
				};

		shellClient.done = function(req) {
				if (req.readyState == this.DONE_STATE) {
					var result = req.responseText.replace(/^\s*|\s*$/g, '');  // trim whitespace
					return this.fetchResult(result);
					}
				};

		shellClient.runStatement = function() {
				var req = this.getXmlHttpRequest();
				if (!req) {
					document.getElementById('display').innerHTML = "Duh! Some stupid error. Your browser probably doesn't support AJAX. :(";
					return false;
					}
				req.onreadystatechange = function() { shellClient.done(req); };
 
				var params = '';			// build the query parameter string
				params += '&' + 'statement' + '=' + escape(document.getElementById('prompt').innerHTML).replace('+','%2B');
				params += '&' + 'session' + '=' + escape(document.getElementById('shellSessionId').content); 
				params += '&' + 'lol' + '=' + _LOL_MODE; 

				//document.getElementById('notifications').className = 'prompt processing';

				// send the request and tell the user.
				req.open('GET', 'shell.do' + '?' + params, true);
				req.setRequestHeader('Content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
				req.send(null);

				return false;
				};


function toggleLOL(){
		if(_LOL_MODE==0)_LOL_MODE=1;
		else _LOL_MODE=0;
		var _MODE_VALUE=(_LOL_MODE?'on':'off');
		}
		
