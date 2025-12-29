# 🚚 Logistics Transport - Odoo 17 Modulu

Nəqliyyat və Logistika İdarəetmə Modulu (transport module) - Odoo 17 üçün xüsusi hazırlanmış modul.

## layihə Haqqında

Bu modul daşınmaların mənbədən təyinat yerinə qədər izlənməsini təmin edir. Daşıyıcı məlumatları, məhsul detalları, çatdırılma cədvəlləri və PDF hesabatları ilə tam logistika idarəetməsi.

Xüsusiyyətlər
| Daşıyıcı şirkət, əlaqə şəxsi, telefon və email məlumatları |
| Yola çıxma/gəliş tarixləri, müddət hesablanması (tam ədəd) |
| Ölkə, şəhər və ünvan məlumatları |
| Yol, Dəmir yolu, Dəniz, Hava, Multimodal |
| Beynəlxalq ticarət şərtləri (EXW, FOB, CIF və s.) |
| Məhsullar, miqdar, çəki, həcm, qablaşdırma növü |
| Peşəkar transport sənədi çapı |
| Kanban və optimallaşdırılmış siyahı görünüşü |
| Mesajlaşma, qeydlər və aktivitə izləmə |

Texniki Məlumat
| **Odoo Versiyası** | 17.0 |
| **Python Versiyası** | 3.10+ |
| **Lisenziya** | LGPL-3 |
| **Asılılıqlar** | base, mail, product, stock |

Modul Strukturu


custom_addons/
└── logistics_transport/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   └── transport.py
    ├── views/
    │   └── transport_views.xml
    ├── report/
    │   └── transport_report.xml
    ├── security/
    │   └── ir.model.access.csv
    └── static/
        └── description/
            └── icon.png

Tələblər
- Odoo 17.0
- PostgreSQL 12+
- Python 3.10+
- wkhtmltopdf (PDF hesabatları üçün)

Odoo Mənbə Kodunu Klonlayın
git clone https://github.com/odoo/odoo.git --depth 1 --branch 17.0



Modulu Quraşdırın
1. Brauzerdə `http://localhost:8069` açın
2. **Apps** menyusuna daxil olun
3. "Logistics Transport" axtarın
4. **Install** düyməsinə basın

## 📖 İstifadə Qaydası

### Yeni Daşınma Yaratmaq
1. **Logistics Transport** → **Operations** → **Transports**
2. **New** düyməsinə basın
3. Formu doldurun:
   - Daşıyıcı seçin
   - Mənbə və təyinat məlumatlarını daxil edin
   - Nəqliyyat növünü seçin
   - Tarixləri təyin edin
4. **Products** tabında məhsulları əlavə edin
5. **Save** edin

### Status Axını
```
Draft → Confirmed → In Transit → Delivered → Cancelled


### PDF Hesabat
- Daşınma formasında **Print** düyməsinə basın
- "Transport Document" seçin

## 🔧 Konfiqurasiya Faylları

### odoo.conf.example
[options]
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
addons_path = odoo/odoo/addons,odoo/addons,custom_addons
http_port = 8069