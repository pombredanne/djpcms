/*jshint node: true */
/*global config:true, task:true, process:true*/
module.exports = function(grunt) {
    "use strict";
    var libs = {
            djpcms: {
                src: ['srcjs/libs/jquery.form.js',
                      'srcjs/libs/jquery.cookie.js',
                      'srcjs/start.js',
                      'srcjs/core.js',
                      'srcjs/callbacks.js',
                      'srcjs/utils.js',
                      'srcjs/deco/ajax.js',
                      'srcjs/deco/autocomplete.js',
                      'srcjs/deco/button.js',
                      'srcjs/deco/collapse.js',
                      'srcjs/deco/misc.js',
                      'srcjs/deco/showdown.js',
                      'srcjs/jquery/commonancestor.js',
                      'srcjs/close.js'],
                dest: 'djpcms/media/djpcms/djpcms.js'
            },
            table: {
                src: ['srcjs/table/start.js',
                      'srcjs/table/color.js',
                      'srcjs/table/djptable.js',
                      'srcjs/table/close.js'],
                dest: 'djpcms/media/djpcms/djptable.js',
            }
    };
    //
    function for_each(obj, callback) {
        for(var p in obj) {
            if(obj.hasOwnProperty(p)) {
                callback.call(obj[p], p);
            }
        }
    }
    //
    // Preprocess libs
    for_each(libs, function (name) {
        var options = this.options;
        if(options && options.banner) {
            options.banner = grunt.file.read(options.banner);
        }
    });
    //
    function uglify_libs () {
        var result = {};
        for_each(libs, function (name) {
            result[name] = {dest: this.dest.replace('.js', '.min.js'),
                            src: [this.dest]};
        });
        return result;
    }
    //
    // js hint all libraries
    function jshint_libs () {
        var result = {
                gruntfile: "Gruntfile.js",
                options: {
                    browser: true,
                    expr: true,
                    globals: {
                        jQuery: true,
                        $$: true,
                        lux: true,
                        requirejs: true,
                        require: true,
                        exports: true,
                        console: true,
                        DOMParser: true,
                        Showdown: true,
                        prettyPrint: true,
                        module: true,
                        ok: true,
                        equal: true,
                        test: true,
                        asyncTest: true,
                        start: true
                    }
                }
        };
        for_each(libs, function (name) {
            result[name] = this.dest;
        });
        return result;
    }
    //
    // This Grunt Config Entry
    // -------------------------------
    //
    // Initialise Grunt with all tasks defined above
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        concat: libs,
        uglify: uglify_libs(),
        jshint: jshint_libs()
    });
    //
    // These plugins provide necessary tasks.
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-concat');
    //grunt.loadNpmTasks('grunt-contrib-nodeunit');
    //grunt.loadNpmTasks('grunt-contrib-watch');
    //grunt.loadNpmTasks('grunt-docco');
    //
    grunt.registerTask('gruntfile', 'jshint Gruntfile.js',
            ['jshint:gruntfile']);
    grunt.registerTask('default',
            ['concat', 'jshint', 'uglify']);
    //
    for_each(libs, function (name) {
        grunt.registerTask(name,
                'Compile & lint "' + name + '" library into ' + this.dest,
                ['concat:' + name, 'jshint:' + name, 'uglify:' + name]);
    });
};
