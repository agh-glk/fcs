import django_tables2 as tables
from models import Task
import itertools
from django_tables2.utils import A


class TaskTable(tables.Table):
    row_number = tables.Column(empty_values=())
    name = tables.LinkColumn('show_task', args=[A('id')])

    def __init__(self, *args, **kwargs):
        super(TaskTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count(1)

    def render_row_number(self):
        return '%d' % next(self.counter)

    def render_type(self, value):
        return ', '.join(map(lambda x: str(x), value.all()))

    def render_expire_date(self, value):
        return value.strftime("%Y-%m-%d %H:%M")

    def render_created(self, value):
        return value.strftime("%Y-%m-%d %H:%M")

    class Meta:
        model = Task
        attrs = {"class": "table"}
        order_by = "created"
        fields = ('row_number', 'name', 'id', 'priority', 'whitelist', 'blacklist', 'max_links', 'type', 'created',
                  'expire_date', 'active', 'finished')

