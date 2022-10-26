from django.urls import path
from api.views import (
                    OperatorList, BotList, OperatorDetail, DailyReport, BlackListView, ReceiveFileView,
                    WeeklyReport, MonthlyReport, DashBoardMonthly, BlackListDetail,
                    BotDetail, DashBoardDaily, DashBoardWeekly, Statistics,
                    ChangePasswordView, SendPhoto, RequestPasswordResetEmail,
                    SetNewPasswordAPIView, PasswordTokenCheckAPI, ReceivePhotoView
                    )
urlpatterns = [
                path('operator/', OperatorList().as_view(), name='operators-list'),
                path('operator/<int:operator_id>/', OperatorDetail.as_view(), name = 'operator-detail'),
                path('bot/', BotList.as_view(), name='bots-list'),
                path('bot/<int:pk>/', BotDetail.as_view(), name = 'bot-detail'),
                path('daily-message/', DailyReport.as_view(), name = 'daily-message' ),
                path('weekly-message/', WeeklyReport.as_view(), name = 'weekly-message' ),
                path('monthly-message/', MonthlyReport.as_view(), name = 'monthly-message' ),
                path('dashboard-daily/<int:slavebot_id>/', DashBoardDaily.as_view(), name = 'dashboard-daily'),
                path('dashboard-weekly/<int:slavebot_id>/', DashBoardWeekly.as_view(), name = 'dashboard-weekly'),
                path('dashboard-monthly/<int:slavebot_id>/', DashBoardMonthly.as_view(), name = 'dashboard-monthly'),
                path('black-list/', BlackListView.as_view(), name = 'black-list'),
                path('black-list-detail/<int:chat_id>/', BlackListDetail.as_view(), name = 'black-list-detail'),
                path('statistics/', Statistics.as_view(), name = 'statistics'),
                path('change-password/', ChangePasswordView.as_view(), name = 'change-password'),
                path('request-reset-email/', RequestPasswordResetEmail.as_view(), name="request-reset-email"),
                path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
                path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
                path('send-photo/', SendPhoto.as_view(), name=' '),
                path('save/photo/', ReceivePhotoView.as_view(), name='save-photo'),
                path("save/file/", ReceiveFileView.as_view(), name="save-file")
                
            ]
