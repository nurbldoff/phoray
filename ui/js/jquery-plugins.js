function getCaretPosition (element) {
  var iCaretPos = 0;

  // IE Support
  if (document.selection) {
    element.focus ();
    var oSel = document.selection.createRange ();
    oSel.moveStart ('character', -element.value.length);
    iCaretPos = oSel.text.length;
  }

  // Firefox support
  else if (element.selectionStart || element.selectionStart == '0')
    iCaretPos = element.selectionStart;

  return (iCaretPos);
}


function setCaretPosition(elem, caretPos) {
    if (elem != null) {
        if (elem.createTextRange) {
            var range = elem.createTextRange();
            range.move('character', caretPos);
            range.select();
        } else {
            if (elem.selectionStart) {
                elem.focus();
                elem.setSelectionRange(caretPos, caretPos);
            } else elem.focus();
        }
    }
}


var increase = function (value, position) {
    var sign = "";
    if (value[0] == "-") {
        sign = "-";
        value = value.substr(1);
        position--;
    }
    var digit = parseInt(value[position]);
    if (position < value.length && digit !== NaN) {
        if (digit == 9) {  // overflow to the left
            if (position > 0) {
                var prevpos = value[position - 1] == "."? position - 2 : position - 1,
                    tmp = increase(value, prevpos);
                value = tmp.value.substr(0, tmp.position + 1) + 0 + value.substr(position + 1);
            } else {
                value = "10" + value.substr(1);
                position++;
            }
        } else {
            value = value.substr(0, position) + (digit + 1) + value.substr(position + 1);
        }
    }
    // // Strip leading zeroes
    // while (value[0] == "0" && value.length > 0) {
    //     value = value.substr(1);
    //     position --;
    // }
    return {value: sign + value, position: position + sign.length};
};

var decrease = function (value, position) {
    var sign = "";
    if (value[0] == "-") {
        sign = "-";
        value = value.substr(1);
        position--;
    }
    var digit = parseInt(value[position]);
    if (position >= 0 && position < value.length && digit !== NaN) {
        if (digit == 0) {
            if (position > 0) {
                var prevpos = value[position - 1] == "."? position - 2 : position - 1,
                    tmp = decrease(value, prevpos);
                value = tmp.value.substr(0, position) + 9 + value.substr(position + 1);
            }
        } else {
            value = value.substr(0, position) + (digit - 1) + value.substr(position + 1);
        }
    }
    return {value: sign + value, position: position + sign.length};
};

var updown = function (evt) {
    var up = 38, down = 40,
        key = evt.keyCode,
        $target = $(evt.target);
    if (key == up) {
        evt.preventDefault();
        var pos = getCaretPosition($target.get(0)),
            res = increase($target.val(), pos);
        $target.val(res.value);
        setCaretPosition($target.get(0), res.position);
        $target.change();
    } else if (key == down) {
        evt.preventDefault();
        var pos = getCaretPosition($target.get(0)),
            res = decrease($target.val(), pos);
        // while (parseInt(res.value[0]) === 0 && res.value.length > 1) {
        //     res.value = res.value.substr(1);
        //     res.position --;
        // }
        $target.val(res.value);
        setCaretPosition($target.get(0), res.position);
        $target.change();
    }
};