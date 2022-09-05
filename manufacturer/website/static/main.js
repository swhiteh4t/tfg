function hide(){
    warning = document.getElementsByClassName("alert alert-warning")
    sucess = document.getElementsByClassName("alert alert-success")
    for (var i=0;i<sucess.length;i+=1){
        sucess[i].style.display = 'none';
      }
    for (var i=0;i<warning.length;i+=1){
        warning[i].style.display = 'none';
      }
}