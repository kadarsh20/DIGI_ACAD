
$('textarea').each(function () {
  this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
  }).on('input', function () {
  this.style.height = 'auto';
  this.style.height = (this.scrollHeight) + 'px';
});
function printfiles(){
    var x = document.getElementById("selectedfiles");
    console.log("hi")
    var output = "Uploaded Files,<br>";
    if ('files' in x) {
        if (x.files.length == 0) {
            output = "Select one or more files.";
        } else {
        for (var i = 0; i < x.files.length; i++) {
            var file = x.files[i];
            if ('name' in file) {
                output += file.name + "<br>";
            }
        }
        }
    }
    else {
        x.setAttribute(value="None") //to check if it is correct or not
        output += "Either no files were uploaded or Some files types are not supported.";
        output  += "<br>The path of the selected file: " + x.value;
    }
    document.getElementById("filesplaceholder").innerHTML = output;
    return true;
}
var count = 2; //Minimum 1 question needs to be added
function addQuestion()
{
    var add = document.getElementById('question-add');
  if(add){
    if (count > 20)
    {
      alert("Not more than 20 Questions are allowed. please either merge questions or create a new test.")
      return true;
    }

    // Create the new text box
    var newInput = document.createElement('textarea');
    newInput.type = 'text';
    newInput.name = 'question-' + count.toString();
    newInput.id = "i"+ count.toString();
    newInput.placeholder = 'Question ' + count.toString();
    newInput.classList.add("input200")
    newInput.style.marginBottom = "20px"
    var divcreate = document.createElement("div");
    divcreate.classList.add('item');

    // Add the new questions
    newInput.appendChild(document.createElement("br"))
    newInput.appendChild(document.createElement("br"))
    divcreate.appendChild(newInput);
    

    add.appendChild(divcreate)
    // Increment the count
    count+=1;
  }
}
function removeQuestion(){
    var idtochoose = 'i' + (count - 1).toString() ;
    console.log(idtochoose)
    document.getElementById(idtochoose).remove()
    count -=1;
}
