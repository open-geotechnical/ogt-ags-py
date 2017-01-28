
from docutils import nodes, utils
from docutils.parsers.rst.roles import set_classes



def rule_type(name, rawtext, text, lineno, inliner, options={}, content=[]):
    print "YES", name, rawtext, text, lineno, inliner, options

    if text == "csv" or text == "data":

        options['class'] = "ags-csv-rule"

        #set_classes(options)
        #html = '<div class="ags_rule_type">%s</div>' % text.upper()
        node = nodes.reference(rawtext, text.upper(), refuri="#",
                           **options)
        return [node], []


    raise ValueError('ags rule_type incorrect value')






def setup(app):
    app.add_role("rule_type", rule_type)
    #app.add_role("data_role", data_role)
    #app.add_config_value('inline_highlight_respect_highlight', True, 'env')

    return {'version': '0.1'}
