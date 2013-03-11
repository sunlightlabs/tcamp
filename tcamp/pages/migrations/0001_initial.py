# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Template'
        db.create_table('pages_template', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('is_path', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('pages', ['Template'])

        # Adding model 'Page'
        db.create_table('pages_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pages', to=orm['pages.Template'])),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content', self.gf('markupfield.fields.MarkupField')(rendered_field=True)),
            ('js', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('content_markup_type', self.gf('django.db.models.fields.CharField')(default=None, max_length=30)),
            ('_content_rendered', self.gf('django.db.models.fields.TextField')()),
            ('css', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('pages', ['Page'])

        # Adding model 'Chunk'
        db.create_table('pages_chunk', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('content', self.gf('markupfield.fields.MarkupField')(rendered_field=True)),
            ('content_markup_type', self.gf('django.db.models.fields.CharField')(default=None, max_length=30)),
            ('_content_rendered', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('pages', ['Chunk'])


    def backwards(self, orm):
        # Deleting model 'Template'
        db.delete_table('pages_template')

        # Deleting model 'Page'
        db.delete_table('pages_page')

        # Deleting model 'Chunk'
        db.delete_table('pages_chunk')


    models = {
        'pages.chunk': {
            'Meta': {'ordering': "('slug',)", 'object_name': 'Chunk'},
            '_content_rendered': ('django.db.models.fields.TextField', [], {}),
            'content': ('markupfield.fields.MarkupField', [], {'rendered_field': 'True'}),
            'content_markup_type': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'pages.page': {
            'Meta': {'ordering': "('path',)", 'object_name': 'Page'},
            '_content_rendered': ('django.db.models.fields.TextField', [], {}),
            'content': ('markupfield.fields.MarkupField', [], {'rendered_field': 'True'}),
            'content_markup_type': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30'}),
            'css': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'js': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pages'", 'to': "orm['pages.Template']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'pages.template': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Template'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_path': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['pages']