from django.conf.urls.defaults import *

import views


urlpatterns = patterns('',
    url(r'^$', views.admin, name='pontoon.admin'),
    url(r'^project/$', views.manage_project, name='pontoon.admin.project.new'),
    url(r'^project/(?P<name>.+)/$', views.manage_project, name='pontoon.admin.project'),
    url(r'^delete/(?P<pk>\d+)/$', views.delete_project, name='pontoon.admin.project.delete'),
    url(r'^repository/$', views.update_from_repository, name='pontoon.admin.repository.update'),
    url(r'^transifex/$', views.update_from_transifex, name='pontoon.admin.transifex.update'),
)
