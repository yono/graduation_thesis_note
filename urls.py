from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^graduate/', include('graduate.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    (r'^note/$','graduate.note.views.index'),
    (r'^note/(?P<user_nick>.*)/$','graduate.note.views.user'),
    #(r'^note/user/(?<user_id>\d+)/(?<note_id>\d+)/$','graduate.note.views.note'),
)
