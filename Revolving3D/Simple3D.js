function Point3D(xVal, yVal, zVal)
{
	var _x=xVal!=undefined?xVal:0;
	var _y=yVal!=undefined?yVal:0;
	var _z=zVal!=undefined?zVal:0;
	var myScene=null;
	var xIdx;
	var yIdx;
	var zIdx;
	var xIdx2D;
	var yIdx2D;

	this.setupWithScene=function(scene)
	{
		myScene=scene;

		var idx=scene.setupPoint(_x, _y, _z);
		var i3=idx*3;
		var i2=idx*2;

		xIdx=i3;
		yIdx=i3+1;
		zIdx=i3+2;

		xIdx2D=i2;
		yIdx2D=i2+1;
	}

	this.getSceneIdx=function()
	{
		return mySceneIdx;
	}

	this.getX=function()
	{
		return _x;
	}

	this.setX=function(value)
	{
		if(myScene!=null)
			myScene.points3D[xIdx]=value;

		_x=value;
	}

	this.getY=function()
	{
		return _y;
	}

	this.setY=function(value)
	{
		if(myScene!=null)
			myScene.points3D[yIdx]=value;

		_y=value;
	}

	this.getZ=function()
	{
		return _z;
	}

	this.setZ=function(value)
	{
		if(myScene!=null)
			myScene.points3D[zIdx]=value;

		_z=value;
	}

	this.getX2D=function()
	{
		return myScene.points2D[xIdx2D];
	}

	this.getY2D=function()
	{
		return myScene.points2D[yIdx2D];
	}

	//this.__defineGetter__("sceneIdx", this.getSceneIdx);
	//this.__defineGetter__("x", this.getX);
	//this.__defineGetter__("y", this.getY);
	//this.__defineGetter__("z", this.getZ);
	//this.__defineSetter__("x", this.setX);
	//this.__defineSetter__("y", this.setY);
	//this.__defineSetter__("z", this.setZ);
	//this.__defineGetter__("x2D", this.getX2D);
	//this.__defineGetter__("y2D", this.getY2D);
	Object.defineProperty(this, "sceneIdx", {get: this.getSceneIdx,enumerable: true,	configurable: true,	writeable: false});
	Object.defineProperty(this, "x",  		{get: this.getX, set: this.setX,  enumerable: true,    configurable: true, writeable: true});
    Object.defineProperty(this, "x",  		{get: this.getX, set: this.setX,  enumerable: true,    configurable: true, writeable: true});
	Object.defineProperty(this, "x",  		{get: this.getX, set: this.setX,  enumerable: true,    configurable: true, writeable: true});
	Object.defineProperty(this, "x2D",		{get: this.getX2D, enumerable: true,	configurable: true,	writeable: false});
	Object.defineProperty(this, "y2D",		{get: this.getY2D, enumerable: true,	configurable: true,	writeable: false});
}

function Line3D()
{
	this.colour="#AAAAAA";
	this.points=[];
	this.startPoint=new Point3D();
	this.endPoint=new Point3D();

	this.addToScene=function(scene)
	{
		for(var i=0;i<this.points.length;i++)
		{
			this.points[i].setupWithScene(scene);
		}
	}

	this.addPoint=function(point)
	{
		this.points[this.points.length]=point;
	}

	this.render=function(context)
	{
		context.beginPath();
		context.strokeStyle=this.colour;

		for(var i=0;i<this.points.length;i++)
		{
			context.lineTo(this.points[i].x2D, this.points[i].y2D);	
		}

		context.stroke();
	}
}

function Scene3D(canvas)
{
	this.matrix=new Matrix3D();
	this.rotationX=0;
	this.rotationY=0;
	this.scale=1;
	this.focalLength=1000;
	this.context=canvas.getContext("2d");
	this.sceneWidth=canvas.width;
	this.sceneHeight=canvas.height;
	this.points3D=[];
	this.points2D=[];
	this.numPoints=0;
	this.items=[];

	this.context.fillStyle="rgba(0, 0, 0, 1);";
	this.context.fillRect(0, 0, this.sceneWidth, this.sceneHeight);

	this.addItem=function(item)
	{
		this.items[this.items.length]=item;
		item.addToScene(this);
	}

	this.setupPoint=function(x, y, z)
	{
		var returnVal=this.numPoints;

		this.points2D[this.points2D.length]=0;
		this.points2D[this.points2D.length]=0;

		this.points3D[this.points3D.length]=x;
		this.points3D[this.points3D.length]=y;
		this.points3D[this.points3D.length]=z;

		this.numPoints++;

		return returnVal;
	}

	this.render=function()
	{
		var halfWidth=this.sceneWidth*0.5;
		var halfHeight=this.sceneHeight*0.5;

		this.matrix.identity();
		this.matrix.scale(this.scale, this.scale, this.scale);
		this.matrix.rotateX(this.rotationX);
		this.matrix.rotateY(this.rotationY);
		this.matrix.translate(0, 0, 1000);

		var transformed=this.matrix.transformArray(this.points3D);

		for(var i=0;i<this.numPoints;i++)
		{
			var i3=i*3;
			var i2=i*2;

			var x=transformed[i3];
			var y=transformed[i3+1];
			var z=transformed[i3+2];

			var scale=this.focalLength/(z+this.focalLength);

			this.points2D[i2]=x*scale+halfWidth;
			this.points2D[i2+1]=y*scale+halfHeight;
		}

		var startTime=(new Date()).getTime();
		this.context.save();
		this.context.fillStyle="rgb(0, 0, 0);";
		this.context.fillRect(0, 0, this.sceneWidth, this.sceneHeight);

	
		for(var i=0;i<this.items.length;i++)
		{
			this.items[i].render(this.context);
		}

		this.context.restore();
		console.log((new Date()).getTime()-startTime);
	}
}