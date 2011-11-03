

INNER_BLOCK_TEMPLATES = {
    'half-half': '''\
<div class="yui3-g">
    <div class="yui3-u-2">
    </div>
    <div class="yui3-u-2">
    </div>
</div>''',
    'third-third-third': '''\
<div class="yui3-g">
    <div class="yui3-u-3">
    </div>
    <div class="yui3-u-3">
    </div>
    <div class="yui3-u-3">
    </div>
</div>'''
}


def inner_block_choices(bf):
    return (('','---------'),) +\
            tuple(((m,m) for m in sorted(INNER_BLOCK_TEMPLATES)))