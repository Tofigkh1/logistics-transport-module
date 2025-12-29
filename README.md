# Odoo 17.0 Projesi

Bu proje Odoo 17.0 ERP sistemini içermektedir.

## Kurulum Tamamlandı

✅ Python 3.10 sanal ortam  
✅ Odoo 17.0 kaynak kodu  
✅ Tüm Python bağımlılıkları  

## PostgreSQL Kurulumu (Gerekli)

Odoo çalışması için PostgreSQL veritabanı gereklidir:

### Yöntem 1: PostgreSQL Kurulumu (Önerilen)
1. https://www.postgresql.org/download/windows/ adresinden PostgreSQL indirin
2. Kurulum sırasında şifre olarak `odoo` belirleyin
3. pgAdmin'i açın ve yeni bir kullanıcı oluşturun:
   - Kullanıcı adı: `odoo`
   - Şifre: `odoo`
   - Superuser: Evet

### Yöntem 2: Docker ile
```bash
docker run -d --name odoo-postgres -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres -p 5432:5432 postgres:15
```

## Odoo'yu Başlatma

### PowerShell ile:
```powershell
cd C:\Users\BEST16\Desktop\odoo-project
.\venv\Scripts\Activate.ps1
cd odoo
python odoo-bin -c ..\odoo.conf
```

### Batch dosyası ile:
```
start_odoo.bat
```

## Erişim

Sunucu başladıktan sonra:
- URL: http://localhost:8069
- Master Password: admin

## Proje Yapısı

```
odoo-project/
├── venv/               # Python sanal ortam
├── odoo/               # Odoo kaynak kodu
├── custom_addons/      # Özel modülleriniz için
├── odoo.conf           # Odoo yapılandırma dosyası
├── start_odoo.bat      # Windows başlatma scripti
└── README.md           # Bu dosya
```

## Özel Modül Geliştirme

`custom_addons/` klasörüne yeni modüller ekleyebilirsiniz.

Örnek modül yapısı:
```
custom_addons/
└── my_module/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    ├── views/
    └── security/
```

## Faydalı Komutlar

```powershell
# Modül güncelleme
python odoo-bin -c ..\odoo.conf -u my_module

# Tüm modülleri yükleme
python odoo-bin -c ..\odoo.conf -i base

# Geliştirici modu ile çalıştırma
python odoo-bin -c ..\odoo.conf --dev=all
```
