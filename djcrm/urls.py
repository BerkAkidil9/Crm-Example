from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, include
from leads.views import landing_page, LandingPageView, SignupView, CustomLoginView, CustomPasswordResetView, CustomPasswordResetConfirmView, CustomPasswordResetDoneView, EmailVerificationSentView, EmailVerificationView, EmailVerificationSuccessView, EmailVerificationFailedView, debug_email_test

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='landing-page'),
    path('leads/', include('leads.urls', namespace='leads')),
    path('agents/', include('agents.urls', namespace='agents')),
    path('organisors/', include('organisors.urls', namespace='organisors')),
    path('ProductsAndStock/', include('ProductsAndStock.urls', namespace='ProductsAndStock')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('finance/', include('finance.urls', namespace='finance')),
    path('tasks/', include('tasks.urls', namespace='tasks')),
    path('activity-log/', include('activity_log.urls', namespace='activity_log')),
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-email-sent/', EmailVerificationSentView.as_view(), name='verify-email-sent'),
    path('verify-email/<uuid:token>/', EmailVerificationView.as_view(), name='verify-email'),
    path('verify-email-success/', EmailVerificationSuccessView.as_view(), name='verify-email-success'),
    path('verify-email-failed/', EmailVerificationFailedView.as_view(), name='verify-email-failed'),
    path('reset-password/', CustomPasswordResetView.as_view(), name='reset-password'),
    path('password-reset-done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('debug/email-test/', debug_email_test, name='debug-email-test'),
]

# Always serve media files (static files are handled by WhiteNoise)
# In production on Render, uploaded files are stored on ephemeral filesystem
# and will be lost on redeploy. Consider using cloud storage (S3/Cloudinary) for persistent media.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)