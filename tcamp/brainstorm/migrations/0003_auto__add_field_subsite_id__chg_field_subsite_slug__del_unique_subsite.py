# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # OMFG Get ready, we're going to change the primary key!
        # Doing bad things, disabling triggers
        db.execute("ALTER TABLE brainstorm_idea DISABLE TRIGGER ALL;")

        # Dropping foreign key constraint
        db.delete_foreign_key('brainstorm_idea', 'subsite_id')
        db.execute('DROP INDEX brainstorm_idea_subsite_id_like')
        db.delete_index('brainstorm_idea', ['subsite_id'])

        # Removing primary key on 'Subsite', fields ['slug']
        db.delete_primary_key(u'brainstorm_subsite')

        # Adding primary key field 'Subsite.id'
        db.add_column(u'brainstorm_subsite', u'id',
                      self.gf('django.db.models.fields.IntegerField')(blank=True, null=True))

        # WOW. Have to manually create AutoFields. Thanks Django!
        db.execute('CREATE SEQUENCE brainstorm_subsite_id_seq;')
        db.execute("UPDATE brainstorm_subsite SET id = nextval('brainstorm_subsite_id_seq');")
        db.execute("ALTER TABLE brainstorm_subsite ALTER COLUMN id SET DEFAULT nextval('brainstorm_subsite_id_seq');")
        db.execute('ALTER SEQUENCE brainstorm_subsite_id_seq OWNED BY brainstorm_subsite.id;')
        db.execute("SELECT setval('brainstorm_subsite_id_seq', q.i) FROM(SELECT MAX(id) i FROM brainstorm_subsite) q;")

        # Now make it the pk
        db.create_primary_key('brainstorm_subsite', ['id'])

        # Updating foreign key values
        db.execute('''UPDATE brainstorm_idea idea
                      SET subsite_id = subsite.id
                      FROM brainstorm_subsite subsite
                      WHERE(idea.subsite_id = subsite.slug);''')

        # Casting the fk to an integer
        db.execute("ALTER TABLE brainstorm_idea ALTER COLUMN subsite_id TYPE integer USING CAST(subsite_id AS integer);")

        # Re-adding foreign key constraint
        fk_sql = db.foreign_key_sql('brainstorm_idea', 'subsite_id', 'brainstorm_subsite', 'id')
        print fk_sql
        db.execute(fk_sql)

        # Changing field 'Subsite.slug' to a plain old slugfield
        db.alter_column(u'brainstorm_subsite', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=50))

        # Adding unique constraint on 'Subsite', fields ['slug']
        db.create_unique(u'brainstorm_subsite', ['slug'])

        # Re-enabling triggers
        db.execute("ALTER TABLE brainstorm_idea ENABLE TRIGGER ALL;")

    def backwards(self, orm):
        # Deleting field 'Subsite.id'
        db.delete_column(u'brainstorm_subsite', u'id')


        # Changing field 'Subsite.slug'
        db.alter_column(u'brainstorm_subsite', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=50, primary_key=True))
        # Adding primary key on 'Subsite', fields ['slug']
        db.create_primary_key(u'brainstorm_subsite', ['slug'])


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
        u'brainstorm.idea': {
            'Meta': {'ordering': "('-score',)", 'object_name': 'Idea'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'downvotes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subsite': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ideas'", 'to': u"orm['brainstorm.Subsite']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'upvotes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ideas'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'brainstorm.subsite': {
            'Meta': {'object_name': 'Subsite'},
            'allow_downvote': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'downvote_label': ('django.db.models.fields.CharField', [], {'default': "'Vote Down'", 'max_length': '255'}),
            'downvotes_label': ('django.db.models.fields.CharField', [], {'default': "'{} Down'", 'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idea_label': ('django.db.models.fields.CharField', [], {'default': "'idea'", 'max_length': '128'}),
            'ideas_per_page': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'post_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'scoring_algorithm': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'theme': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'upvote_label': ('django.db.models.fields.CharField', [], {'default': "'Vote Up'", 'max_length': '255'}),
            'upvotes_label': ('django.db.models.fields.CharField', [], {'default': "'{} Up'", 'max_length': '255', 'blank': 'True'}),
            'voted_label': ('django.db.models.fields.CharField', [], {'default': "'Clear Vote'", 'max_length': '255'}),
            'voting_status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'brainstorm.vote': {
            'Meta': {'ordering': "('-timestamp',)", 'unique_together': "(('user', 'idea'),)", 'object_name': 'Vote'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idea': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': u"orm['brainstorm.Idea']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'idea_votes'", 'to': u"orm['auth.User']"}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['brainstorm']