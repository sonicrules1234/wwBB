class htmlhelper() :
    def __init__(self) :
        self.html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
            }
        self.header = ""
        self.footer = ""
    def tag(self, tagname, data) :
        return "<%s>%s</%s>" % (tagname, data, tagname)
    def html(self, arg, inner=False) :
        return '<?xml version="1.0" encoding="utf-8" ?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\n"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml">%s</html>' % (self.choose(arg, inner))
    def p(self, arg, inner=False) :
        return self.tag("p", self.choose(arg, inner))
    def br() :
        return "<br />"
    def head(self, arg, inner=False) :
        return self.tag("head", self.choose(arg, inner))
    def title(self, arg, inner=False) :
        return self.tag("title", self.choose(arg, inner))
    def body(self, arg, inner=False) :
        return self.tag("body", self.choose(self.header+arg+self.footer, inner))
    def choose(self, text,arg) :
        if arg :
            return self.html_escape(text)
        else : return text
    def a(self, href, text=None, inner=False) :
        if text == None :
            text = href
        if text != href :
            text == self.choose(text, inner)
        return '<a href="%s">%s</a>' % (href, text)
    def html_escape(self, text):
        """Produce entities within text."""
        return "".join(self.html_escape_table.get(c,c) for c in text)
    def strong(self, arg, inner=False) :
        return self.tag("strong", self.choose(arg, inner))
    def em(self, arg, inner=False) :
        return self.tag("em", self.choose(arg, inner))
    def setHeader(self, arg) :
        self.header = arg
    def setFooter(self, arg) :
        self.footer = arg
