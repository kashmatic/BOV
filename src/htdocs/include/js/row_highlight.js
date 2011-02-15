window.onload = function(){
	ConvertRowsToLinks('list');
}

function ConvertRowsToLinks(xTableId){

	var rows = document.getElementById(xTableId).getElementsByTagName('tr');
   
	for(i=0;i<rows.length;i++){
		var link = rows[i].getElementsByTagName('a')
		if(link.length == 1){
			rows[i].onclick = new Function(\"document.location.href='\" + link[0].href + \"'\");
			rows[i].onmouseover = new Function(\"this.className='highlight'\");
			rows[i].onmouseout = new Function(\"this.className=''\");	
		}
	}
}