/*jshint node: true */
/*global config:true, task:true, process:true*/
module.exports = function(grunt) {
    var libs = ['srcjs/libs/jquery.form.js',
                'srcjs/libs/jquery.cookie.js'],
        djpcms = ['srcjs/start.js',
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
        extra = [];
    grunt.initConfig({
        concat: {
            djpcms: {
                dest: 'djpcms/media/djpcms/djpcms.js',
                src: djpcms
            },
            dist: {
                dest: 'djpcms/media/djpcms/djpcms.js',
                src: libs.concat(djpcms)
            }
        },
        min: {
            dist: {
                dest: 'djpcms/media/djpcms/djpcms-min.js',
                src: ['djpcms/media/djpcms/djpcms.js']
            }
        },
        lint: {
            dist: 'djpcms/media/djpcms/djpcms.js',
            grunt: "grunt.js"
        },
        jshint: {
            options: {
                browser: true
            },
            globals: {
                jQuery: true,
                console: true,
                DOMParser: true
            }
        },
        uglify: {}
    });
    // Default task.
    grunt.registerTask('grunt', 'lint:grunt');
    grunt.registerTask('default', 'concat:dist lint:dist min:dist');
};