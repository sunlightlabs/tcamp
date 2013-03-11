# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'SponsorshipLevel.content_type'
        db.delete_column(u'camp_sponsorshiplevel', 'content_type_id')

        # Deleting field 'SponsorshipLevel.object_id'
        db.delete_column(u'camp_sponsorshiplevel', 'object_id')

        # Adding M2M table for field events on 'SponsorshipLevel'
        db.create_table(u'camp_sponsorshiplevel_events', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sponsorshiplevel', models.ForeignKey(orm[u'camp.sponsorshiplevel'], null=False)),
            ('event', models.ForeignKey(orm[u'sked.event'], null=False))
        ))
        db.create_unique(u'camp_sponsorshiplevel_events', ['sponsorshiplevel_id', 'event_id'])

        # Deleting field 'Sponsor.content_type'
        db.delete_column(u'camp_sponsor', 'content_type_id')

        # Deleting field 'Sponsor.object_id'
        db.delete_column(u'camp_sponsor', 'object_id')

        # Adding field 'Sponsor.event'
        db.add_column(u'camp_sponsor', 'event',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='sponsors', to=orm['sked.Event']),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'SponsorshipLevel.content_type'
        raise RuntimeError("Cannot reverse this migration. 'SponsorshipLevel.content_type' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'SponsorshipLevel.object_id'
        raise RuntimeError("Cannot reverse this migration. 'SponsorshipLevel.object_id' and its values cannot be restored.")
        # Removing M2M table for field events on 'SponsorshipLevel'
        db.delete_table('camp_sponsorshiplevel_events')


        # User chose to not deal with backwards NULL issues for 'Sponsor.content_type'
        raise RuntimeError("Cannot reverse this migration. 'Sponsor.content_type' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Sponsor.object_id'
        raise RuntimeError("Cannot reverse this migration. 'Sponsor.object_id' and its values cannot be restored.")
        # Deleting field 'Sponsor.event'
        db.delete_column(u'camp_sponsor', 'event_id')


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
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'camp.sponsor': {
            'Meta': {'ordering': "('-sponsorship_level__order', '-order')", 'object_name': 'Sponsor'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sponsors'", 'to': u"orm['sked.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'sponsorship_level': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['camp.SponsorshipLevel']"}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        u'camp.sponsorshiplevel': {
            'Meta': {'ordering': "('-order',)", 'object_name': 'SponsorshipLevel'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'events': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sponsorship_levels'", 'symmetrical': 'False', 'to': u"orm['sked.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': "'0'"}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'sked.event': {
            'Meta': {'ordering': "('-start_date',)", 'object_name': 'Event'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sked_events'", 'to': u"orm['auth.User']"}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "'event'", 'max_length': '64'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'registration_is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'registration_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'session_label': ('django.db.models.fields.CharField', [], {'default': "'session'", 'max_length': '64'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['camp']