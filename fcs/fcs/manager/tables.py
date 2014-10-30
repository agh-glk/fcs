import django_tables2 as tables
from models import Task
from django_tables2.utils import A
import django_tables2.rows


class ColoredBoundRows(django_tables2.rows.BoundRows):
    def __iter__(self):
        for record in self.data:
            row = django_tables2.rows.BoundRow(record, table=self.table)
            row.style = 'some_class'
            yield row

    def __getitem__(self, key):
        container = ColoredBoundRows if isinstance(key, slice) else django_tables2.rows.BoundRow
        return container(self.data[key], table=self.table)


class ColoredRowsTable(tables.Table):
    def __init__(self, *args, **kwargs):
        super(ColoredRowsTable, self).__init__(*args, **kwargs)
        self.rows = ColoredBoundRows(data=self.data, table=self)


class TaskTable(ColoredRowsTable):
    name = tables.LinkColumn('show_task', args=[A('id')])
    active = tables.Column(visible=False)
    finished = tables.Column(visible=False)

    def __init__(self, *args, **kwargs):
        super(TaskTable, self).__init__(*args, **kwargs)

    def render_expire_date(self, value):
        return value.strftime("%Y-%m-%d %H:%M")

    def render_created(self, value):
        return value.strftime("%Y-%m-%d %H:%M")

    def render_whitelist(self, value):
        return self.parse_value(value, 20, 2)

    def render_blacklist(self, value):
        return self.parse_value(value, 20, 2)

    def render_start_links(self, value):
        return self.parse_value(value, 20, 2)

    def render_mime_type(self, value):
        return self.parse_value(value, 20, 2)

    def parse_value(self, value, max_len, max_lines):
        lines = [val if len(val) <= max_len else val[:max_len] + '...' for val in value.split()]
        return '\n'.join(lines if len(lines) <= max_lines else lines[:max_lines] + ['...'])

    class Meta:
        model = Task
        attrs = {"class": "table"}
        order_by = "created"
        fields = ('id', 'name', 'priority', 'start_links', 'whitelist', 'blacklist', 'max_links', 'mime_type', 'created',
                  'expire_date', 'active', 'finished')
        template = "colored_table.html"
