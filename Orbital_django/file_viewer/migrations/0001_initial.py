# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-28 08:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import file_viewer.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_time', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('page_index', models.IntegerField()),
                ('height_percent', models.FloatField()),
                ('width_percent', models.FloatField()),
                ('top_percent', models.FloatField()),
                ('left_percent', models.FloatField()),
                ('frame_color', models.CharField(max_length=18)),
                ('num_like', models.IntegerField(default=0)),
                ('annotator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AnnotationReply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_time', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('num_like', models.IntegerField(default=0)),
                ('replier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('reply_to_annotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='file_viewer.Annotation')),
                ('reply_to_annotation_reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reply_set', to='file_viewer.AnnotationReply')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_time', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('num_like', models.IntegerField(default=0)),
                ('commenter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1028)),
                ('num_visit', models.IntegerField(default=0)),
                ('collectors', models.ManyToManyField(blank=True, related_name='collected_document_set', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UniqueFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_field', models.FileField(upload_to=file_viewer.models.upload_to)),
                ('md5', models.CharField(max_length=32)),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='unique_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='file_viewer.UniqueFile'),
        ),
        migrations.AddField(
            model_name='comment',
            name='document_this_comment_belongs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='file_viewer.Document'),
        ),
        migrations.AddField(
            model_name='comment',
            name='reply_to_comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reply_set', to='file_viewer.Comment'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='document_this_annotation_belongs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='file_viewer.Document'),
        ),
    ]
