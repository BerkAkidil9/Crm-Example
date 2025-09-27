from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, include
from leads.views import landing_page, LandingPageView, SignupView, CustomLoginView, EmailVerificationSentView, EmailVerificationView, EmailVerificationFailedView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='landing-page'),
    path('leads/', include('leads.urls', namespace='leads')),
    path('agents/', include('agents.urls', namespace='agents')),
    path('organisors/', include('organisors.urls', namespace='organisors')),
    path('ProductsAndStock/', include('ProductsAndStock.urls', namespace='ProductsAndStock')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('finance/', include('finance.urls', namespace='finance')),
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-email-sent/', EmailVerificationSentView.as_view(), name='verify-email-sent'),
    path('verify-email/<uuid:token>/', EmailVerificationView.as_view(), name='verify-email'),
    path('verify-email-failed/', EmailVerificationFailedView.as_view(), name='verify-email-failed'),
    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('password-reset-done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)