from django.db import models
from django.contrib.auth.models import User


class ChartProject(models.Model):
    """A project is associated with a burndown chart in the UI."""
    name = models.CharField(max_length=256)
    start_date = models.DateField('start date')
    end_date = models.DateField('end date')
    admin = models.ForeignKey(User)

    def __unicode__(self):
        return self.project_name

class Task(models.Model):
    """ Tasks are components of projects. """
    project = models.ForeignKey(ChartProject)
    task_name = models.CharField(max_length=500)
    end_date = models.DateField('end date', null=True, blank=True)
    points = models.IntegerField(default=0)
    responsible = models.ForeignKey(User, null=True, blank=True)

    def __unicode__(self):
        return self.task_name

