# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'manager_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'manager', ['User'])

        # Adding M2M table for field groups on 'User'
        m2m_table_name = db.shorten_name(u'manager_user_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'manager.user'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'User'
        m2m_table_name = db.shorten_name(u'manager_user_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'manager.user'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'permission_id'])

        # Adding model 'Quota'
        db.create_table(u'manager_quota', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('max_priority', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('priority_pool', self.gf('django.db.models.fields.IntegerField')(default=100)),
            ('max_tasks', self.gf('django.db.models.fields.IntegerField')(default=50)),
            ('link_pool', self.gf('django.db.models.fields.IntegerField')(default=10000)),
            ('max_links', self.gf('django.db.models.fields.IntegerField')(default=10000)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['manager.User'], unique=True)),
        ))
        db.send_create_signal(u'manager', ['Quota'])

        # Adding model 'CrawlingType'
        db.create_table(u'manager_crawlingtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
        ))
        db.send_create_signal(u'manager', ['CrawlingType'])

        # Adding model 'Task'
        db.create_table(u'manager_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['manager.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('whitelist', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('blacklist', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('max_links', self.gf('django.db.models.fields.IntegerField')(default=1000)),
            ('expire_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'manager', ['Task'])

        # Adding M2M table for field type on 'Task'
        m2m_table_name = db.shorten_name(u'manager_task_type')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('task', models.ForeignKey(orm[u'manager.task'], null=False)),
            ('crawlingtype', models.ForeignKey(orm[u'manager.crawlingtype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['task_id', 'crawlingtype_id'])

        # Adding model 'Service'
        db.create_table(u'manager_service', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['manager.User'])),
            ('type', self.gf('django.db.models.fields.IntegerField')(max_length=2)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=2)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'manager', ['Service'])

        # Adding model 'ServiceUnitPrice'
        db.create_table(u'manager_serviceunitprice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service_type', self.gf('django.db.models.fields.IntegerField')(max_length=2)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=2)),
            ('date_from', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_to', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'manager', ['ServiceUnitPrice'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'manager_user')

        # Removing M2M table for field groups on 'User'
        db.delete_table(db.shorten_name(u'manager_user_groups'))

        # Removing M2M table for field user_permissions on 'User'
        db.delete_table(db.shorten_name(u'manager_user_user_permissions'))

        # Deleting model 'Quota'
        db.delete_table(u'manager_quota')

        # Deleting model 'CrawlingType'
        db.delete_table(u'manager_crawlingtype')

        # Deleting model 'Task'
        db.delete_table(u'manager_task')

        # Removing M2M table for field type on 'Task'
        db.delete_table(db.shorten_name(u'manager_task_type'))

        # Deleting model 'Service'
        db.delete_table(u'manager_service')

        # Deleting model 'ServiceUnitPrice'
        db.delete_table(u'manager_serviceunitprice')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'manager.crawlingtype': {
            'Meta': {'object_name': 'CrawlingType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'max_length': '1'})
        },
        u'manager.quota': {
            'Meta': {'object_name': 'Quota'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_pool': ('django.db.models.fields.IntegerField', [], {'default': '10000'}),
            'max_links': ('django.db.models.fields.IntegerField', [], {'default': '10000'}),
            'max_priority': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'max_tasks': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            'priority_pool': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['manager.User']", 'unique': 'True'})
        },
        u'manager.service': {
            'Meta': {'object_name': 'Service'},
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'type': ('django.db.models.fields.IntegerField', [], {'max_length': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['manager.User']"})
        },
        u'manager.serviceunitprice': {
            'Meta': {'object_name': 'ServiceUnitPrice'},
            'date_from': ('django.db.models.fields.DateTimeField', [], {}),
            'date_to': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'service_type': ('django.db.models.fields.IntegerField', [], {'max_length': '2'})
        },
        u'manager.task': {
            'Meta': {'object_name': 'Task'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'blacklist': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'expire_date': ('django.db.models.fields.DateTimeField', [], {}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_links': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'type': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['manager.CrawlingType']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['manager.User']"}),
            'whitelist': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'manager.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['manager']