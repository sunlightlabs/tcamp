# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Subsite'
        db.create_table('brainstorm_subsite', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('scoring_algorithm', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('post_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('theme', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('idea_label', self.gf('django.db.models.fields.CharField')(default='idea', max_length=128)),
            ('ideas_per_page', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('upvote_label', self.gf('django.db.models.fields.CharField')(default='Vote Up', max_length=255)),
            ('upvotes_label', self.gf('django.db.models.fields.CharField')(default='{} Up', max_length=255, blank=True)),
            ('allow_downvote', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('downvote_label', self.gf('django.db.models.fields.CharField')(default='Vote Down', max_length=255)),
            ('downvotes_label', self.gf('django.db.models.fields.CharField')(default='{} Down', max_length=255, blank=True)),
            ('voted_label', self.gf('django.db.models.fields.CharField')(default='Clear Vote', max_length=255)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('brainstorm', ['Subsite'])

        # Adding model 'Idea'
        db.create_table('brainstorm_idea', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('upvotes', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('downvotes', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('score', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ideas', null=True, to=orm['auth.User'])),
            ('subsite', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ideas', to=orm['brainstorm.Subsite'])),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('brainstorm', ['Idea'])

        # Adding model 'Vote'
        db.create_table('brainstorm_vote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='idea_votes', to=orm['auth.User'])),
            ('idea', self.gf('django.db.models.fields.related.ForeignKey')(related_name='votes', to=orm['brainstorm.Idea'])),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('brainstorm', ['Vote'])

        # Adding unique constraint on 'Vote', fields ['user', 'idea']
        db.create_unique('brainstorm_vote', ['user_id', 'idea_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Vote', fields ['user', 'idea']
        db.delete_unique('brainstorm_vote', ['user_id', 'idea_id'])

        # Deleting model 'Subsite'
        db.delete_table('brainstorm_subsite')

        # Deleting model 'Idea'
        db.delete_table('brainstorm_idea')

        # Deleting model 'Vote'
        db.delete_table('brainstorm_vote')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'brainstorm.idea': {
            'Meta': {'ordering': "('-score',)", 'object_name': 'Idea'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'downvotes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subsite': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ideas'", 'to': "orm['brainstorm.Subsite']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'upvotes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ideas'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'brainstorm.subsite': {
            'Meta': {'object_name': 'Subsite'},
            'allow_downvote': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'downvote_label': ('django.db.models.fields.CharField', [], {'default': "'Vote Down'", 'max_length': '255'}),
            'downvotes_label': ('django.db.models.fields.CharField', [], {'default': "'{} Down'", 'max_length': '255', 'blank': 'True'}),
            'idea_label': ('django.db.models.fields.CharField', [], {'default': "'idea'", 'max_length': '128'}),
            'ideas_per_page': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'post_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'scoring_algorithm': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'primary_key': 'True'}),
            'theme': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'upvote_label': ('django.db.models.fields.CharField', [], {'default': "'Vote Up'", 'max_length': '255'}),
            'upvotes_label': ('django.db.models.fields.CharField', [], {'default': "'{} Up'", 'max_length': '255', 'blank': 'True'}),
            'voted_label': ('django.db.models.fields.CharField', [], {'default': "'Clear Vote'", 'max_length': '255'})
        },
        'brainstorm.vote': {
            'Meta': {'ordering': "('-timestamp',)", 'unique_together': "(('user', 'idea'),)", 'object_name': 'Vote'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idea': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['brainstorm.Idea']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'idea_votes'", 'to': "orm['auth.User']"}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['brainstorm']