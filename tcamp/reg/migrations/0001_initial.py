# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TicketType'
        db.create_table(u'reg_tickettype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sked.Event'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('expires', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('max_tickets', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('price', self.gf('django_extras.db.models.fields.MoneyField')(max_digits=20, decimal_places=2)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('position', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'reg', ['TicketType'])

        # Adding model 'CouponCode'
        db.create_table(u'reg_couponcode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sked.Event'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('discount', self.gf('django_extras.db.models.fields.PercentField')(default=100)),
            ('max_tickets', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'reg', ['CouponCode'])

        # Adding model 'Sale'
        db.create_table(u'reg_sale', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sked.Event'])),
            ('first_name', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('last_name', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('address1', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('address2', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('coupon_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['reg.CouponCode'], null=True, on_delete=models.SET_NULL)),
            ('amount', self.gf('django_extras.db.models.fields.MoneyField')(max_digits=20, decimal_places=2, blank=True)),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('success', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'reg', ['Sale'])

        # Adding model 'Ticket'
        db.create_table(u'reg_ticket', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sked.Event'])),
            ('sale', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['reg.Sale'], null=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['reg.TicketType'])),
            ('barcode', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=36, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('organization', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('twitter', self.gf('django.db.models.fields.CharField')(max_length=127, blank=True)),
            ('website', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('diet_vegetarian', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('diet_vegan', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('diet_gluten_free', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('diet_allergies', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('diet_allergies_desc', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('diet_other', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('diet_other_desc', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('attend_day1', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('attend_day2', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('lobby_day', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ambassador_program', self.gf('django.db.models.fields.CharField')(default='no', max_length=12)),
            ('subscribe', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('success', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal(u'reg', ['Ticket'])


    def backwards(self, orm):
        # Deleting model 'TicketType'
        db.delete_table(u'reg_tickettype')

        # Deleting model 'CouponCode'
        db.delete_table(u'reg_couponcode')

        # Deleting model 'Sale'
        db.delete_table(u'reg_sale')

        # Deleting model 'Ticket'
        db.delete_table(u'reg_ticket')


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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'reg.couponcode': {
            'Meta': {'object_name': 'CouponCode'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'discount': ('django_extras.db.models.fields.PercentField', [], {'default': '100'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sked.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_tickets': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'reg.sale': {
            'Meta': {'object_name': 'Sale'},
            'address1': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'address2': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'amount': ('django_extras.db.models.fields.MoneyField', [], {'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'coupon_code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['reg.CouponCode']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sked.Event']"}),
            'first_name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'reg.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'ambassador_program': ('django.db.models.fields.CharField', [], {'default': "'no'", 'max_length': '12'}),
            'attend_day1': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'attend_day2': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'barcode': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '36', 'blank': 'True'}),
            'diet_allergies': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'diet_allergies_desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'diet_gluten_free': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'diet_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'diet_other_desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'diet_vegan': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'diet_vegetarian': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sked.Event']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'lobby_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'sale': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['reg.Sale']", 'null': 'True'}),
            'subscribe': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'twitter': ('django.db.models.fields.CharField', [], {'max_length': '127', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['reg.TicketType']"}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'reg.tickettype': {
            'Meta': {'ordering': "['position']", 'object_name': 'TicketType'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sked.Event']"}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_tickets': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'price': ('django_extras.db.models.fields.MoneyField', [], {'max_digits': '20', 'decimal_places': '2'})
        },
        u'sked.event': {
            'Meta': {'ordering': "('-start_date',)", 'object_name': 'Event'},
            '_description_rendered': ('django.db.models.fields.TextField', [], {}),
            '_overview_rendered': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sked_events'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'description': ('markupfield.fields.MarkupField', [], {'rendered_field': 'True', 'blank': 'True'}),
            'description_markup_type': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "'event'", 'max_length': '64'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'overview': ('markupfield.fields.MarkupField', [], {'rendered_field': 'True', 'blank': 'True'}),
            'overview_markup_type': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30', 'blank': 'True'}),
            'registration_is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'registration_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'session_label': ('django.db.models.fields.CharField', [], {'default': "'session'", 'max_length': '64'}),
            'session_length': ('timedelta.fields.TimedeltaField', [], {}),
            'session_submission_is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'start_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['reg']