# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Block'
        db.create_table('pages_block', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=255)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(related_name='blocks', to=orm['pages.Page'])),
            ('content', self.gf('markupfield.fields.MarkupField')(rendered_field=True)),
            ('content_markup_type', self.gf('django.db.models.fields.CharField')(default=None, max_length=30)),
            ('_content_rendered', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('pages', ['Block'])

        # Adding field 'Template.content_block'
        db.add_column('pages_template', 'content_block',
                      self.gf('django.db.models.fields.CharField')(default='content', max_length=255),
                      keep_default=False)


        # Changing field 'Template.name'
        db.alter_column('pages_template', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))
        # Removing index on 'Template', fields ['name']
        db.delete_index('pages_template', ['name'])


    def backwards(self, orm):
        # Adding index on 'Template', fields ['name']
        db.create_index('pages_template', ['name'])

        # Deleting model 'Block'
        db.delete_table('pages_block')

        # Deleting field 'Template.content_block'
        db.delete_column('pages_template', 'content_block')


        # Changing field 'Template.name'
        db.alter_column('pages_template', 'name', self.gf('django.db.models.fields.SlugField')(max_length=50))

    models = {
        'pages.block': {
            'Meta': {'object_name': 'Block'},
            '_content_rendered': ('django.db.models.fields.TextField', [], {}),
            'content': ('markupfield.fields.MarkupField', [], {'rendered_field': 'True'}),
            'content_markup_type': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'blocks'", 'to': "orm['pages.Page']"})
        },
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
            'content_block': ('django.db.models.fields.CharField', [], {'default': "'content'", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_path': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['pages']