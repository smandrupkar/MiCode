// forked from MikkoH's "RadioHead3D(Contiguous Line)" http://jsdo.it/MikkoH/RadioHead3DContiguous
var MAX_ROT=Math.PI*0.3;
var canvas;
var scene;
var mouseX, mouseY;
var stats;

function onInit()
{
try
{
    
	document.onmousemove=onMouseMove;
    document.ontouchmove=onMouseMove;

	canvas=document.getElementById("mainCanvas");
    
	scene=new Scene3D(canvas);
	scene.scale=8;

	var numLinesSegments=pointData.length/4;

	var line=new Line3D();

	line.colour="rgb(255, 0, 0)";

	for(var i=0;i<numLinesSegments;i++)
	{
		var i4=i*4;
		
		line.addPoint(new Point3D(pointData[i4], pointData[i4+1], pointData[i4+2]));
	}

	scene.addItem(line);
    
    stats=new Stats();
    stats.domElement.style.position="absolute";
    stats.domElement.style.top="0px";
    document.getElementById("container").appendChild(stats.domElement);
    
	setInterval(onRender, 16);
	}
	catch(exception)
	{
	  alert (exception);
	}
}

function onMouseMove(ev)
{
    if(ev.touches!==null)
    {
        mouseX=ev.touches[0].pageX;
        mouseY=ev.touches[0].pageY;
    }
    else
    {
        mouseX=ev.pageX;
        mouseY=ev.pageY;   
    }
}
var i=0;
function onRender()
{
	//scene.rotationX=i/canvas.height*MAX_ROT*2-MAX_ROT;
        if(i==500)
    {
        i=i*-1;
    }
	scene.rotationY=i/canvas.width*MAX_ROT*2-MAX_ROT;
    i=i+1;

	scene.render();
    stats.update();
}