<!DOCTYPE html>
<html>
<head>
  <style>
fieldset { margin-bottom: 1em; }
input { display: block; margin-bottom: .25em; }
#print-output {
  width: 100%;
}
.print-output-line {
  white-space: pre;
  padding: 5px;
  font-family: monaco, monospace;
  font-size: .7em;
}

</style>
  <script src="http://code.jquery.com/jquery-latest.js"></script>

<link rel="stylesheet" type="text/css" href="css/style.css" />
</head>


<body>

<div id = "trainer">
Type your answer and press enter.
<form>
  <fieldset>
    <label id="problem" for="target">Problem</label>
    <input id="target" type="text" />
  </fieldset>
</form>
<div id="error">Incorrect!</div>

</div>

<div id = "login">
<form>
	<label for="uname">Username</label>
	<input id="uname" type="text" />
	<label for="pw">Password</label>
	<input id="pw" type="text" />
	<button id="login_button">Login</button>
</form>
</div>

<div id = "instructions">
<p>Welcome to your training session.  Get ready to perform some arithmetic problems.  It is important that you try to solve the problem quickly, so as soon as you know the answer please type it in and press enter.</p>
<p>Please, no guessing.</p>
<p>Press the 'Continue' button when you are ready to begin training.</p>
<form>
<button id="ready_button">Continue</button>
</form>


</div>






<script>
var problemCount=0;
var blockCount=0;
var problems=[];
var onset = 0;
var subject = "1";
var solution = 0;
var n1 = 0;
var n2 = 0;
var prevErr = false;

function shuffle(array) {
    var tmp, current, top = array.length;

    if(top) while(--top) {
        current = Math.floor(Math.random() * (top + 1));
        tmp = array[current];
        array[current] = array[top];
        array[top] = tmp;
    }

    return array;
}

function setProblem(p) {
	n = p.split('|');
	//alert(n);
	pstring = n[0] + " + " + n[1];
	n1 = Number(n[0]);
	n2 = Number(n[1]);
	solution = n1 + n2;
	$('#problem').html(pstring);
	var currentTime = new Date();
	onset = currentTime.getTime();
	problemCount++;
}

$(document).ready(function() {
	$('#trainer').toggle();
	$('#instructions').toggle();
});

$('#ready_button').click(function(event) {
	event.preventDefault();
	setProblem(problems[problemCount]);
	$('#instructions').toggle();
	$('#trainer').toggle();
	$('#error').toggle();
	$('#target').focus();

});

$('#login_button').click(function(event) {
	event.preventDefault();
	subject = $('#uname').val();
	var password = $('#pw').val();


	$.get("checkCredentials.php?uname=" + subject + "&pw=" + password, function(data) {
		if (data == 1) {
			$.get("getProblems.php?subject=" + subject, function(data) { 
			problems = data.split(',');
			$('#instructions').toggle();
			$('#login').toggle();

			});
		}
		else {
			alert("Login Failed - Try again");

		}
	});
});

$('#target').keypress(function(event) {
  if (event.keyCode == '13') {
	event.preventDefault();
	var currentTime = new Date();
	millis = currentTime.getTime();
	RT = millis - onset;

	//var solution = n1 + n2;
	var s_sol = $('#target').val();

	if (s_sol == solution) {
		if (prevErr) {
			$('#error').toggle();
		}
		ACC = 1;
		prevErr= false;
	}
	else {
		if (prevErr != true) {
			$('#error').toggle();
		}
		ACC = 0;
		prevErr = true;
		problemCount--;
	}
	$('#target').val("");


	//if we've done one loop of the problems
	if (problemCount >= problems.length) {
		blockCount++;
		//see if we're done all the blocks
		if (blockCount == 10) {
			$('#problem').html("All done - see you tomorrow!");
			$('#target').toggle();
			alert("All done - see you tomorrow!");
		}
		else {
			//otherwise restart the loop
			problemCount = 0;
			problems = shuffle(problems);
			setProblem(problems[problemCount]);
		}
	}
	else {
 		setProblem(problems[problemCount]);
	}


	$.get("setProblems.php?n1=" + n1 + "&n2=" + n2 +"&subject= " + subject + "&RT=" + RT + "&ACC=" + ACC + "&RESP=" + s_sol);

	//alert(millis);
   }
});
</script>


</body>
</html>
