/**
 * Format a number and return a string based on input settings
 * @param {Number} number The input number to format
 * @param {Number} decimals The amount of decimals
 * @param {String} decPoint The decimal point, defaults to the one given in the lang options
 * @param {String} thousandsSep The thousands separator, defaults to the one given in the lang options
 */
//$.djpcms.numberFormat = function (number, decimals, decPoint, thousandsSep) {
//    var lang = defaultOptions.lang,
//        // http://kevin.vanzonneveld.net/techblog/article/javascript_equivalent_for_phps_number_format/
//        n = number, c = isNaN(decimals = mathAbs(decimals)) ? 2 : decimals,
//        d = decPoint === undefined ? lang.decimalPoint : decPoint,
//        t = thousandsSep === undefined ? lang.thousandsSep : thousandsSep, s = n < 0 ? "-" : "",
//        i = String(pInt(n = mathAbs(+n || 0).toFixed(c))),
//        j = i.length > 3 ? i.length % 3 : 0;
//
//    return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) +
//        (c ? d + mathAbs(n - i).toFixed(c).slice(2) : "");
//};
/**
 * Return an object containing the formatted currency and a flag
 * indicating if it is negative
 */
$.djpcms.format_currency = function (s, precision) {
    if (!precision) {
        precision = 3;
    }
    s = s.replace(/, /g, '');
    var c = parseFloat(s),
        isneg = false,
        decimal = false,
        de = '',
        i,
        cs,
        cn,
        d,
        k,
        N,
        mul,
        atom;
    //
    if (isNaN(c)) {
        cs = s;
    } else {
        cs = s.split('.', 2);
        if (c < 0) {
            isneg = true;
            c = Math.abs(c);
        }
        cn = parseInt(c, 10);
        if (cs.length === 2) {
            de = cs[1];
            if (!de) {
                de = '.';
            } else {
                decimal = true;
                de = c - cn;
            }
        }
        if (decimal) {
            mul = Math.pow(10, precision);
            atom = String(parseInt(c * mul, 10) / mul).split(".")[1];
            de = '';
            decimal = false;
            for (i = 0; i < Math.min(atom.length, precision); i++) {
                de += atom[i];
                if (parseInt(atom[i], 10) > 0) {
                    decimal = true;
                }
            }
            if (decimal) {
                de = '.' + de;
            }
        }
        cn += "";
        N  = cn.length;
        cs = "";
        for (i = 0; i < N; i++) {
            cs += cn[i];
            k = N - i - 1;
            d = parseInt(k / 3, 10);
            if (3 * d === k && k > 0) {
                cs += ',';
            }
        }
        cs += de;
        if (isneg) {
            cs = '-' + cs;
        } else {
            cs = String(cs);
        }
    }
    return {
        value: cs,
        negative: isneg
    };
};