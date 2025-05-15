from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms
from django.utils.html import format_html
from django.template.response import TemplateResponse

from shifts.models import Shift
from shifts.service import ShiftService


class OptimizeShiftsForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )


class ShiftAdmin(admin.ModelAdmin):
    list_display = ('user', 'warehouse', 'day_of_week', 'start_time', 'end_time', 'is_optimized')
    list_filter = ('day_of_week', 'warehouse', 'user', 'is_optimized')
    search_fields = ('user__username', 'warehouse__name')
    date_hierarchy = 'created_at'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('optimize-shifts/', self.admin_site.admin_view(self.optimize_shifts_view), name='optimize-shifts'),
        ]
        return custom_urls + urls
    
    def optimize_shifts_view(self, request):
        if request.method == 'POST':
            form = OptimizeShiftsForm(request.POST)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data.get('end_date')
                
                service = ShiftService()
                result = service.optimize_shifts(
                    start_date=start_date,
                    end_date=end_date
                )
                
                if result['success']:
                    messages.success(request, format_html(
                        'Оптимизация успешно завершена. Оптимизировано смен: {}<br>'
                        'Сообщение: {}',
                        len(result['shifts']), 
                        result['message']
                    ))
                else:
                    messages.error(request, format_html(
                        'Ошибка при оптимизации смен: {}',
                        result['message']
                    ))
                
                return redirect('admin:shifts_shift_changelist')
        else:
            form = OptimizeShiftsForm()
        
        context = {
            'form': form,
            'title': 'Оптимизация смен',
            'opts': self.model._meta,
        }
        return render(request, 'admin/shifts/optimize_shifts.html', context)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_optimize_button'] = True
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Shift, ShiftAdmin) 