y = document.getElementsByClassName("btnino");
for (i = 0; i < y.length; i++) {
  var newItem = document.createElement("DIV");       
  newItem.innerHTML = '<span></span><span></span><span></span><span></span><span></span>';
  newItem.className = ('hoverino');
  x = document.getElementsByClassName("btnino")[i];
  x.insertBefore(newItem, x.childNodes[0]);
}
