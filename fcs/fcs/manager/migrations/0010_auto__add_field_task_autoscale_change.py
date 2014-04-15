# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Task.autoscale_change'
        db.add_column(u'manager_task', 'autoscale_change',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Task.autoscale_change'
        db.delete_column(u'manager_task', 'autoscale_change')


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
        u'manager.crawler': {
            'Meta': {'object_name': 'Crawler'},
            'address': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timeouts': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'manager.mailsent': {
            'Meta': {'object_name': 'MailSent'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tasks': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['manager.Task']", 'symmetrical': 'False'})
        },
        u'manager.quota': {
            'Meta': {'object_name': 'Quota'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_pool': ('django.db.models.fields.IntegerField', [], {'default': '1000000'}),
            'max_links': ('django.db.models.fields.IntegerField', [], {'default': '100000'}),
            'max_priority': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'max_tasks': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'urls_per_time': ('django.db.models.fields.IntegerField', [], {'default': '10000'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['manager.User']", 'unique': 'True'})
        },
        u'manager.task': {
            'Meta': {'object_name': 'Task'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'autoscale_change': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'blacklist': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'expire_date': ('django.db.models.fields.DateTimeField', [], {}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_data_download': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_server_spawn': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'max_links': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'default': "'text/html'", 'max_length': '250'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'server': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['manager.TaskServer']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'start_links': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['manager.User']"}),
            'whitelist': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        u'manager.taskserver': {
            'Meta': {'object_name': 'TaskServer'},
            'address': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'crawlers': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['manager.Crawler']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
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
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['manager']