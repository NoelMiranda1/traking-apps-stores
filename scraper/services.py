from google_play_scraper import app as google_app
import requests
import certifi
import os
from .models import AppInfo, AppToMonitor
from datetime import datetime

# Configuración para certificados SSL (macOS)
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

def format_timestamp(timestamp):
    """
    Converts a timestamp to formatted date MMM DD, YYYY
    """
    try:
        if not timestamp or timestamp == 0:
            return "Unknown"

        if isinstance(timestamp, str):
            timestamp = int(timestamp)

        if timestamp < 10**10:
            timestamp *= 1000

        while timestamp > 10**13:
            timestamp = timestamp // 1000

        dt = datetime.fromtimestamp(timestamp / 1000)
        return dt.strftime('%b %d, %Y')
    except Exception:
        return "Unknown"

def format_ios_date(date_str):
    """
    Formats an iOS (App Store) ISO date to MMM DD, YYYY format
    """
    try:
        if not date_str:
            return "Unknown"
        
        dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        return dt.strftime('%b %d, %Y')
    except Exception:
        return "Unknown"

def get_android_app_version(package_name):
    """
    Obtiene la versión actual de una aplicación de Google Play Store
    """
    try:
        result = google_app(package_name)
        info = {
            'version': result.get('version', 'Desconocido'),
            'app_name': result.get('title', package_name),
            'last_updated': format_timestamp(result.get('updated')),
            'store': 'google_play',
            'app_id': package_name
        }
        print(f"[ANDROID] {package_name} -> {info}")  # DEBUG
        return info
    except Exception as e:
        print(f"[ANDROID][ERROR] {package_name} -> {str(e)}")
        return {
            'error': f'Error obteniendo información de Google Play: {str(e)}',
            'store': 'google_play',
            'app_id': package_name
        }

def get_ios_app_version(app_id, country='us'):
    """
    Obtiene la versión actual de una aplicación de App Store
    """
    try:
        url = f'https://itunes.apple.com/lookup?id={app_id}&country={country}'
        response = requests.get(url, verify=certifi.where())
        data = response.json()
        
        if data['resultCount'] > 0:
            app_data = data['results'][0]
            info = {
                'version': app_data.get('version', 'Desconocido'),
                'app_name': app_data.get('trackName', app_id),
                'last_updated': format_ios_date(app_data.get('currentVersionReleaseDate')),
                'store': 'app_store',
                'app_id': app_id
            }
            print(f"[iOS] {app_id} -> {info}")  # DEBUG
            return info
        else:
            print(f"[iOS][NOT FOUND] {app_id}")
            return {
                'error': 'No se encontró información de la aplicación',
                'store': 'app_store',
                'app_id': app_id
            }
    except Exception as e:
        print(f"[iOS][ERROR] {app_id} -> {str(e)}")
        return {
            'error': f'Error obteniendo información de App Store: {str(e)}',
            'store': 'app_store',
            'app_id': app_id
        }

def check_all_apps():
    results = []

    android_apps = AppToMonitor.objects.filter(store='google_play')
    ios_apps = AppToMonitor.objects.filter(store='app_store')

    for app in android_apps:
        result = get_android_app_version(app.app_id)
        if 'error' not in result:
            try:
                app_info = AppInfo.objects.create(**result)
                results.append(app_info)
            except Exception as e:
                print(f"[ANDROID][DB ERROR] {app.app_id} -> {str(e)}")

    for app in ios_apps:
        result = get_ios_app_version(app.app_id)
        if 'error' not in result:
            try:
                app_info = AppInfo.objects.create(**result)
                results.append(app_info)
            except Exception as e:
                print(f"[iOS][DB ERROR] {app.app_id} -> {str(e)}")

    return results
