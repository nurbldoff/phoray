/**
 * @author nurbldoff
 */

THREE.OrthographicAspectCamera = function ( width, aspect, near, far ) {

	THREE.Camera.call( this );

	this.width = width;
        this.aspect = aspect;
	this.near = ( near !== undefined ) ? near : 0.1;
	this.far = ( far !== undefined ) ? far : 2000;

	this.updateProjectionMatrix();

};

THREE.OrthographicAspectCamera.prototype = Object.create( THREE.Camera.prototype );

THREE.OrthographicAspectCamera.prototype.updateProjectionMatrix = function () {

	this.left = -this.width / 2;
	this.right = this.width / 2;
	this.top = this.width / this.aspect / 2;
	this.bottom = - this.width / this.aspect / 2;

	this.projectionMatrix.makeOrthographic( this.left, this.right, this.top, this.bottom, this.near, this.far );

};
