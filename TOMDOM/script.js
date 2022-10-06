document.addEventListener("DOMContentLoaded", 
function(){
//let list = document.getElementsByTagName("li");
//let list = document.getElementsByClassName("mybutton");

let list = document.querySelectorAll(".mybutton");
let para = document.querySelector(".paragraph");

for(let i = 0; list.length ; i++)
{
list[i].addEventListener('click', function(){
list[i].style.color = "green";
para.innerHTML = list[i].innerHTML;
  for(let j= 0; list.length; j++)
  {
    if (j != i)
     list[j].style.color = "black";
     
  }// end of inner for loop

});
} // end of outer for loop

list[2].style.color = "red";

});
