ko.numericObservable = function(initialValue) {
    var _actual = ko.observable(initialValue);

    var result = ko.dependentObservable({
        read: function() {
            return _actual();
        },
        write: function(newValue) {
            var parsedValue = parseFloat(newValue) || 0;
            console.log(newValue, parsedValue);
            _actual(isNaN(parsedValue) ? newValue : parsedValue);
        }
    });

    return result;
};

ko.observableVector = function(x, y, z) {

    var self = this;

    self.x = ko.numericObservable(x),
    self.y = ko.numericObservable(y),
    self.z = ko.numericObservable(z);

    var result = ko.computed({
        read: function () {
            return {x: self.x(), y: self.y(), z: self.z()};
        },
        write: function (nx, ny, nz) {
            self.x(nx);
            self.y(ny);
            self.z(nz);
        }
    }); //.extend({ throttle: 1 });

    result.x = self.x;
    result.y = self.y;
    result.z = self.z;

    return result;
};

// wrapper for a computed observable that can pause its subscriptions
// from http://www.knockmeout.net/2011/04/pausing-notifications-in-knockoutjs.html
ko.pauseableComputed = function(evaluatorFunction, evaluatorFunctionTarget) {
    var _cachedValue = "";
    var _isPaused = ko.observable(false);

    //the computed observable that we will return
    var result = ko.computed(function() {
        if (!_isPaused()) {
            //call the actual function that was passed in
            return evaluatorFunction.call(evaluatorFunctionTarget);
        }
        return _cachedValue;
    }, evaluatorFunctionTarget);

    //keep track of our current value and set the pause flag to release our actual subscriptions
    result.pause = function() {
        _cachedValue = this();
        _isPaused(true);
    }.bind(result);

    //clear the cached value and allow our computed observable to be re-evaluated
    result.resume = function() {
        _cachedValue = "";
        _isPaused(false);
    };

    return result;
};


ko.extenders.offsetUpdater = function (target, parent) {
    parent.position.subscribe(function (newpos) {
        target.x(newpos.x);
        target.y(newpos.y);
        target.z(newpos.z);
    });
};

ko.extenders.representation = function (target, parent, scn) {

    // size.subscribe(function (size) {
    //     console.log("size changed", size);
    //     mesh.scale.x = size.x;
    //     mesh.scale.y = size.y;
    //     scene.render();
    // });

    // THREE.js representation
    var repr = new THREE.Object3D();
    var mesh = new THREE.Mesh(
        new THREE.CubeGeometry( 1, 1, 0.1 ),
        new THREE.MeshLambertMaterial( { color: 0xFF0000 } )
    );
    repr.add(mesh);
    scn.add(repr);
    scn.render();

    self.position.subscribe(function (position) {
        repr.position.set(position.x, position.y, position.z);
        scn.render();
    });

    self.rotation.subscribe(function (rotation) {
        scn.set_global_rotation(repr, {
            x: rotation.x / 180 * Math.PI,
            y: rotation.y / 180 * Math.PI,
            z: rotation.z / 180 * Math.PI
        });
            scn.render();
    });

    self.remove = function () {
        scn.remove(repr);
        scn.render();
    };

};


// Observable function that forces it to be a number
ko.observable.fn.forceNumeric = function() {
    var underlyingObservable = this;
    if (!this.forceNumericInterceptor) {
        this.forceNumericInterceptor = ko.computed({
            read: this,
            write: function(newValue) {
                var current = underlyingObservable(),
                    valueToWrite = isNaN(newValue) ? 0 : parseFloat(+newValue);

                // if (valueToWrite < 0) {
                //     valueToWrite = 0;
                // }

                //only write if it changed
                if (valueToWrite !== current) {
                    underlyingObservable(valueToWrite);
                } else {
                    //if the rounded value is the same as it was, but a different value was written, force a notification so the current field is updated to the rounded value
                    if (newValue !== current) {
                            underlyingObservable.valueHasMutated();
                    }
                }
            }
        });
    }

    return this.forceNumericInterceptor;
};


// Observable function that forces it to be a number other than zero
ko.observable.fn.forceNonZero = function() {
    var underlyingObservable = this;
    if (!this.forceNumericInterceptor) {
        this.forceNumericInterceptor = ko.computed({
            read: this,
            write: function(newValue) {
                var current = underlyingObservable(),
                    valueToWrite = isNaN(newValue) ? 0 : parseFloat(+newValue);

                if (valueToWrite == 0) {
                    valueToWrite = current;
                    console.log("Whoops, value can't be zero.");
                }

                //only write if it changed
                if (valueToWrite !== current) {
                    underlyingObservable(valueToWrite);
                } else {
                    //if the rounded value is the same as it was, but a different value was written, force a notification so the current field is updated to the rounded value
                    if (newValue !== current) {
                            underlyingObservable.valueHasMutated();
                    }
                }
            }
        });
    }

    return this.forceNumericInterceptor;
};


// Observable function that forces it to be an integer
ko.observable.fn.forceInteger = function() {
    var underlyingObservable = this;
    if (!this.forceNumericInterceptor) {
        this.forceNumericInterceptor = ko.computed({
            read: this,
            write: function(newValue) {
                var current = underlyingObservable(),
                    valueToWrite = isNaN(newValue) ? 0 : parseInt(+newValue);

                if (valueToWrite !== current) {
                    underlyingObservable(valueToWrite);
                } else {
                    if (newValue !== current) {
                        underlyingObservable.valueHasMutated();
                    }
                }
            }
        });
    }

    return this.forceNumericInterceptor;
};
