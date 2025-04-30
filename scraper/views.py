from django.shortcuts import render, redirect
from django.contrib import messages
from .models import AppInfo, AppToMonitor
from .services import check_all_apps, format_timestamp, format_ios_date
from django.db.models import Max
from django.http import HttpResponse
from openpyxl import Workbook
from datetime import datetime

def export_to_excel(request):
    # Crear un nuevo libro de Excel
    wb = Workbook()
    
    # Crear hoja para Google Play
    ws_android = wb.active
    ws_android.title = "Google Play Apps"
    ws_android.append(['Nombre', 'ID', 'Versión', 'Última actualización'])
    
    # Obtener y escribir datos de apps de Android
    android_apps = AppInfo.objects.filter(
        store='google_play',
        created_at__in=AppInfo.objects.filter(
            store='google_play'
        ).values('app_id').annotate(
            max_created=Max('created_at')
        ).values_list('max_created', flat=True)
    ).order_by('app_name')
    
    for app in android_apps:
        ws_android.append([
            app.app_name,
            app.app_id,
            app.version,
            app.last_updated
        ])
    
    # Crear hoja para iOS
    ws_ios = wb.create_sheet("iOS Apps")
    ws_ios.append(['Nombre', 'ID', 'Versión', 'Última actualización'])
    
    # Obtener y escribir datos de apps de iOS
    ios_apps = AppInfo.objects.filter(
        store='app_store',
        created_at__in=AppInfo.objects.filter(
            store='app_store'
        ).values('app_id').annotate(
            max_created=Max('created_at')
        ).values_list('max_created', flat=True)
    ).order_by('app_name')
    
    for app in ios_apps:
        ws_ios.append([
            app.app_name,
            app.app_id,
            app.version,
            app.last_updated
        ])
    
    # Ajustar el ancho de las columnas
    for ws in [ws_android, ws_ios]:
        for column in ws.columns:
            max_length = 0
            column = list(column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column[0].column_letter].width = adjusted_width
    
    # Crear la respuesta HTTP con el archivo Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=app_versions_{}.xlsx'.format(
        datetime.now().strftime('%Y%m%d_%H%M%S')
    )
    
    wb.save(response)
    return response

def app_list(request):
    if request.method == 'POST':
        if 'update' in request.POST:
            # Actualizar información de las apps
            check_all_apps()
            messages.success(request, 'Información de apps actualizada correctamente')
        elif 'add_app' in request.POST:
            # Agregar nueva app
            app_id = request.POST.get('app_id', '').strip()
            store = request.POST.get('store', '')
            
            if app_id and store:
                try:
                    AppToMonitor.objects.create(app_id=app_id, store=store)
                    check_all_apps()
                    messages.success(request, f'App {app_id} agregada y actualizada correctamente')
                except Exception as e:
                    messages.error(request, f'Error al agregar la app: {str(e)}')
            else:
                messages.error(request, 'Por favor complete todos los campos')
        elif 'export' in request.POST:
            return export_to_excel(request)
    
    # Obtener las apps más recientes de cada tipo usando una subconsulta
    android_apps = AppInfo.objects.filter(
        store='google_play'
    ).values('app_id').annotate(
        max_created=Max('created_at')
    ).values_list('max_created', flat=True)

    ios_apps = AppInfo.objects.filter(
        store='app_store'
    ).values('app_id').annotate(
        max_created=Max('created_at')
    ).values_list('max_created', flat=True)

    # Obtener los registros completos usando las fechas máximas
    android_apps = AppInfo.objects.filter(
        store='google_play',
        created_at__in=android_apps
    ).order_by('app_name')

    ios_apps = AppInfo.objects.filter(
        store='app_store',
        created_at__in=ios_apps
    ).order_by('app_name')

    # Obtener las apps configuradas para monitoreo
    monitored_android_apps = AppToMonitor.objects.filter(store='google_play')
    monitored_ios_apps = AppToMonitor.objects.filter(store='app_store')
    
    context = {
        'android_apps': android_apps,
        'ios_apps': ios_apps,
        'monitored_android_apps': monitored_android_apps,
        'monitored_ios_apps': monitored_ios_apps,
    }
    return render(request, 'scraper/app_list.html', context)
