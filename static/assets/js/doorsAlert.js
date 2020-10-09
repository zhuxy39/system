$(document).ready(function(){
	$("#openAlert").load("",function(response,status){
		if(status=="success" & response[0].status=='open')
		{
			var result="";
			for(var i=0;i<response.length;i++)
			{
				result+="<td id=number>"+response[i].id+"</td><td>东校区</td><td id=building>"+response[i].building+"</td><td id=class>"+response[i].classroom+"</td><td id=useTime>"+responce[i].useTime+"</td><td id=operation>"+response[i].Operatype+"</td><td><a href="+"javascript:deal('open');"+">处理提交</a></td>";
			}
		}
	});
	$("#closeAlert").load("",function(response,status){
		if(status=="success" & response[0].status=='close')
		{
			var result="";
			for(var i=0;i<response.length;i++)
			{
				result+="<td id=number>"+response[i].id+"</td><td>东校区</td><td id=building>"+response[i].building+"</td><td id=class>"+response[i].classroom+"</td><td id=useTime>"+responce[i].useTime+"</td><td id=operation>"+response[i].Operatype+"</td><td><a href="+"javascript:deal('close');"+">处理提交</a></td>";
			}
		}
	});
});

function deal(String status){
	   alert("处理已提交！");
	$.ajax({
		type:'post',
		cache:false,
		url:"/Seaching/",
		data:{
		'csrfmiddlewaretoken':getCookie('csrftoken'),
		'id':$("#number").val(),
		'building':$("#building").val(),
		'classroom':$("#class").val(),
		'time':$("#useTime").val(),
		'operation':$("#operation").val(),
		'status': status;
	    },
		success:function(data)
		{
			var resultSet="";
		    if (response[0].status=='open')
			{
				for(var i=0;i<data.length;i++)
			    {
				      resultSet+="<td id=number>"+response[i].id+"</td><td>东校区</td><td id=building>"+response[i].building+"</td><td id=class>"+response[i].classroom+"</td><td id=useTime>"+responce[i].useTime+"</td><td id=operation>"+response[i].Operatype+"</td><td><a href="+"javascript:deal('open');"+">处理提交</a></td>";
			    }
				$("#openAlert").html(resultSet);
			}
			else
			{
				for(var i=0;i<data.length;i++)
			    {
				      resultSet+="<td id=number>"+response[i].id+"</td><td>东校区</td><td id=building>"+response[i].building+"</td><td id=class>"+response[i].classroom+"</td><td id=useTime>"+responce[i].useTime+"</td><td id=operation>"+response[i].Operatype+"</td><td><a href="+"javascript:deal('close');"+">处理提交</a></td>";
			    }
				$("#closeAlert").html(resultSet);
			}
		}
	})
	return false;
}