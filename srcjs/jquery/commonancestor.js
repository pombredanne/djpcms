/**
 * Common Ancestor jQuery plugin
 */
$.fn.commonAncestor = function () {
    if (!this.length) {
        return $([]);
    }
    var parents = [],
        minlen = Infinity,
        i,
        j,
        p,
        equal;
    //
    this.each(function () {
        var curparents = $(this).parents();
        parents.push(curparents);
        minlen = Math.min(minlen, curparents.length);
    });
    //
    $.each(parents, function (i, p) {
        parents[i] = p.slice(p.length - minlen);
    });
    // Iterate until equality is found
    for (i = 0; i < parents[0].length; i++) {
        p = parents[0][i];
        equal = true;
        for (j = 1; j < parents.length; j++) {
            if (parents[j][i] !== p) {
                equal = false;
                break;
            }
        }
        if (equal) {
            return $(p);
        }
    }
    return $([]);
};