from werkzeug.routing import BaseConverter

class ListConverter(BaseConverter):

    def to_python(self, value):
            return [int(id) for id in value.split('+')]

    def to_url(self, values):
            return '+'.join(BaseConverter.to_url(value)
                        for value in values)
