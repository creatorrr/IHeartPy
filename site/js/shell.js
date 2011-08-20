/*
** Initialize Objects
*/

var _LOL_MODE=0;
var _THEME=0;

	var shellEditor = CodeMirror.fromTextArea(document.getElementById("prompt"), {
				value: document.getElementById("display").value,
				mode: {
					name: "python",
					version: 2,
					singleLineStringErrors: false},
				theme: 'neat',
				lineNumbers: false,
				indentUnit: 4,
				gutter: true,
				tabMode: "shift",
				matchBrackets: true,
				onKeyEvent: function(i, event) {
								var statement = shellEditor.getValue();
								if (/*Ctrl+Enter*/ event.type=="keydown" && event.keyCode == 13 && (event.ctrlKey || event.metaKey) && !event.altKey) {
								event.stop();
								shellEditor.setValue(shellEditor.getValue()+'\n');
								pos={}
								pos.line=shellEditor.lineCount()-1;
								pos.ch=0;
								shellEditor.setCursor(pos);
									}
								else if (/* enter */ event.type=="keypress" && event.keyCode == 13 && !event.altKey && !event.shiftKey) {
								event.stop();
								return shellClient.runStatement();
									}
								}
				});


	var shellDisplay= CodeMirror.fromTextArea(document.getElementById("display"), {
				value: document.getElementById("display").value,
				mode: {
					name: "python",
					version: 2,
					singleLineStringErrors: true},
				theme: 'neat',
				readOnly: "nocursor",
				lineNumbers: true,
				indentUnit: 0,
				tabMode: "default",
				matchBrackets: true
				});

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
				result='\n>>> '+result+'\n';
				shellEditor.setValue('');
				shellDisplay.setValue(shellDisplay.getValue()+result);
				shellDisplay.refresh();
				pos={}
				pos.line=shellDisplay.lineCount()-1;
				pos.ch=0;
				shellDisplay.setCursor(pos);
				shellEditor.focus();
				window.scrollTo(0,window.innerHeight);
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
					document.getElementById('notifications').innerHTML = "Duh! Some stupid error. Your browser probably doesn't support AJAX. :(";
					return false;
					}
				req.onreadystatechange = function() { shellClient.done(req); };
 
				var params = '';			// build the query parameter string
				params += '&' + 'statement' + '=' + (escape(shellEditor.getValue())).replace('+','%2B');
				params += '&' + 'session' + '=' + escape(document.getElementById('shellSessionId').content); 
				params += '&' + 'lol' + '=' + _LOL_MODE; 

				//document.getElementById('notifications').className = 'prompt processing';

				// send the request and tell the user.
				req.open('GET', 'shell.do' + '?' + params, true);
				req.setRequestHeader('Content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
				req.send(null);

				return false;
				};

function shellInit(){
		gutter={}
		gutter.line=0;
		gutter.text=">>>";

		shellEditor.setMarker(gutter.line,gutter.text);
		shellEditor.focus();
		shellDisplay.refresh();
		}

function printer(content){
		var displaySettings="toolbar=yes,location=no,directories=yes,menubar=no,scrollbars=yes,width=650,height=600,left=100,top=25";
		var doc=window.open("","",displaySettings);
		doc.document.open();
		var header='<html><head><title>I &hearts; Py - Print</title><link rel="stylesheet" media="print" href="/css/codemirror/codemirror.css"><link rel="stylesheet" media="print" href="/css/codemirror/theme/neat.css"></head><body onload="self.print()"><pre>';
		var footer='</pre></body></html>';
		doc.document.write(header);
		doc.document.write(content);
		doc.document.write(footer);
		doc.document.close();
		doc.focus();
		}

function toggleLOL(){
		if(_LOL_MODE==0)_LOL_MODE=1;
		else _LOL_MODE=0;
		var _MODE_VALUE=(_LOL_MODE?'on':'off');
		document.getElementById("shellLOL").setAttribute('class',_MODE_VALUE);
		document.getElementById("shellLOL1").setAttribute('class',_MODE_VALUE);		
		}
		
function toggleTheme(){
		if(_THEME==0)_THEME=1;
		else _THEME=0;
		var _THEME_VALUE=(_THEME?'neat':'night');
		
		shellDisplay.setOption("theme",_THEME_VALUE);
		shellEditor.setOption("theme",_THEME_VALUE);		
		}